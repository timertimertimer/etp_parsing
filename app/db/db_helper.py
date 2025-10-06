import csv
from contextlib import contextmanager
from datetime import datetime, timedelta, UTC
from pathlib import PurePath, Path

from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import sessionmaker, Session
from typing import Type, Union, List, Optional

from sqlalchemy import text, select, and_, inspect, literal
from sqlalchemy.orm import joinedload, aliased

from app.crawlers.items import EtpItem
from app.utils.logger import logger
from app.utils.extra import parse_classifiers, sanitize_filename
from app.utils.config import (
    data_path,
    absolute_download_path,
    relative_download_path,
    download_files_from_get_url,
    allowable_formats,
    parse_fedresurs, image_formats, archive_formats,
)
from app.utils.download import DownloadFiles
from app.db.models import (
    Auction,
    ParserStatus,
    TradingFloor,
    Address,
    Region,
    City,
    Counterparty,
    Lot,
    LotPeriod,
    File,
    LegalCase,
    Base,
    DebtorMessage,
    DownloadData,
    CounterpartySRO,
    FileModelType,
    LotCategory,
    StatusType,
    AuctionPropertyType,
)
from app.utils.fedresurs import (
    PersonFedresurs,
    CompanyFedresurs,
    ArbitrManagerFedresurs,
    CounterpartyFedresurs,
    PersonOrganizerFedresurs,
    CompanyOrganizerFedresurs,
    AuctionFedresurs,
)
from app.utils.config import env

logger.info(f"{env.connection_string=}")
engine = create_engine(env.connection_string, echo=False, pool_size=2, max_overflow=0)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DBHelper:
    session: Session | None = None

    @staticmethod
    def create_new_connection():
        DBHelper.session = SessionLocal()
        DBHelper.set_wait_timeout(600)

    @staticmethod
    @contextmanager
    def transaction_scope(commit: bool = True):
        if not DBHelper.session:
            DBHelper.create_new_connection()
        yield DBHelper.session
        if commit:
            DBHelper.session.commit()
        return

    @staticmethod
    def set_wait_timeout(timeout: int = 600):
        DBHelper.session.execute(text(f"SET SESSION wait_timeout = {timeout};"))

    @staticmethod
    def get_latest_lot(
            data_origin_url: str,
            select_keys: set = None,
            day: int = 30,
            property_type: AuctionPropertyType = None,
    ) -> Union[tuple[List, int], None]:
        date_threshold = datetime.now(UTC) - timedelta(days=day)
        if not select_keys:
            select_keys = {Auction.url}  # select only auctions.url
        with DBHelper.transaction_scope(commit=False) as session:
            trading_floor_id = session.scalars(
                select(TradingFloor.id).where(
                    TradingFloor.url == literal(data_origin_url)
                )
            ).first()
            if trading_floor_id is None:
                logger.warning(f"No such trading floor with url {data_origin_url}")
                return None

            stmt = select(*select_keys).where(
                and_(
                    Auction.created_at >= date_threshold,
                    Auction.trading_floor_id == trading_floor_id,
                    Auction.property_type == property_type,
                )
            )
            lots = session.scalars(stmt).all()
            return lots, trading_floor_id

    @staticmethod
    def get_trading_floor_id(crawler_name: str, data_origin_url: str):
        with DBHelper.transaction_scope() as session:
            trading_floor_id = session.scalars(
                select(TradingFloor.id).where(
                    TradingFloor.url == literal(data_origin_url)
                )
            ).first()
            if trading_floor_id is None:
                logger.error(
                    f"TradingFloor not found for URL {data_origin_url}. Skipping"
                )
                return None

            new_parser_status = ParserStatus(
                name=crawler_name, trading_floor_id=trading_floor_id
            )
            session.add(new_parser_status)
        return trading_floor_id

    @staticmethod
    def save_counter_and_duration(
            counter: int,
            duration: float,
            status_active: bool,
            spider_name: str,
            trading_floor_id: int,
    ):
        if status_active is not None:
            with DBHelper.transaction_scope() as session:
                status = StatusType.active if status_active else StatusType.disabled
                session.add(
                    ParserStatus(
                        name=spider_name,
                        trading_floor_id=trading_floor_id,
                        counter=counter,
                        duration=duration,
                        status=status,
                    )
                )
                trading_floor = (
                    session.query(TradingFloor).filter_by(id=trading_floor_id).first()
                )
                if trading_floor.status != status:
                    trading_floor.status = (
                        StatusType.active if status_active else StatusType.disabled
                    )
                logger.info(
                    f"Updated counter and duration for '{spider_name}' to {counter}, {duration}"
                )

    @staticmethod
    def add_regions(
            source_path: PurePath = data_path / "regions_with_oktmo.csv",
    ):
        regions = []
        with DBHelper.transaction_scope() as session:
            existing_oktmos = [r[0] for r in session.query(Region.oktmo).all()]
            with open(source_path, newline="", encoding="utf-8") as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=":")
                for row in reader:
                    if int(row["oktmo"]) not in existing_oktmos:
                        regions.append(
                            Region(oktmo=int(row["oktmo"]), name=row["region"])
                        )
            session.add_all(regions)

    @staticmethod
    def add_addresses(source_path: PurePath = data_path / "addresses.csv"):
        addresses = []
        with DBHelper.transaction_scope() as session:
            regions = {region.name: region.id for region in session.query(Region).all()}
            existing_addresses = [r[0] for r in session.query(Address.name).all()]
            with open(source_path, newline="", encoding="utf-8") as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    if (
                            id_ := regions.get(row["region"])
                                   and row["address"] not in existing_addresses
                    ):
                        addresses.append(Address(region_id=id_, name=row["address"]))
            session.add_all(addresses)

    @staticmethod
    def add_cities(source_path: PurePath = data_path / "cities.csv"):
        cities = []
        with DBHelper.transaction_scope() as session:
            regions = {region.name: region.id for region in session.query(Region).all()}
            existing_cities = [r[0] for r in session.query(City.name).all()]
            with open(source_path, newline="", encoding="utf-8") as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    if (
                            id_ := regions.get(row["region"])
                                   and row["city"] not in existing_cities
                    ):
                        cities.append(City(region_id=id_, name=row["city"]))
            session.add_all(cities)

    @staticmethod
    def add_trading_floors(
            source_path: PurePath = data_path / "trading_floors.csv",
    ):
        trading_floors = []
        with DBHelper.transaction_scope() as session:
            existing_trading_floors = [
                r[0] for r in session.query(TradingFloor.name).all()
            ]
            with open(source_path, newline="", encoding="utf-8") as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    if row["name"] not in existing_trading_floors:
                        trading_floors.append(
                            TradingFloor(name=row["name"], url=row["url"])
                        )
            session.add_all(trading_floors)

    @staticmethod
    def get_addresses():
        with DBHelper.transaction_scope(commit=False) as session:
            return session.query(Address).all()

    @staticmethod
    def get_addresses_with_regions():
        with DBHelper.transaction_scope(commit=False) as session:
            return session.query(Address).options(joinedload(Address.region)).all()

    @staticmethod
    def get_cities_with_regions():
        with DBHelper.transaction_scope(commit=False) as session:
            return session.query(City).options(joinedload(City.region)).all()

    @staticmethod
    def get_all(model: Type[Base]):
        with DBHelper.transaction_scope(commit=False) as session:
            query = session.query(model)
            if model is TradingFloor:
                query = query.options(
                    joinedload(TradingFloor.counterparty).joinedload(
                        Counterparty.sro_memberships
                    )
                )
            elif model is LegalCase:
                query = query.options(
                    joinedload(LegalCase.auctions).joinedload(Auction.debtor)
                )
            elif model is Counterparty:
                query = query.options(joinedload(Counterparty.sro_memberships))
            elif model is Auction:
                query = query.options(
                    joinedload(Auction.trading_floor), joinedload(Auction.legal_case)
                )
            return query.all()

    @staticmethod
    def get_counterparty(
            inn: str | None = None, name: str | None = None, short_name: str | None = None
    ):
        with DBHelper.transaction_scope(commit=False) as session:
            query = session.query(Counterparty)
            if inn:
                query = query.filter(Counterparty.inn == inn)
            elif name:
                query = query.filter(Counterparty.name == name)
            elif short_name:
                query = query.filter(Counterparty.short_name == short_name)
            else:
                return None
            return query.options(joinedload(Counterparty.sro_memberships)).first()

    @staticmethod
    def get_counterparty_sro(counterparty_id: int, sro_counterparty_short_name: str):
        sro_alias = aliased(Counterparty)
        return (
            DBHelper.session.query(CounterpartySRO)
            .join(Counterparty, Counterparty.id == CounterpartySRO.counterparty_id)
            .join(sro_alias, sro_alias.id == CounterpartySRO.sro_id)
            .filter(
                and_(
                    CounterpartySRO.counterparty_id == counterparty_id,
                    sro_alias.short_name == sro_counterparty_short_name,
                )
            )
            .first()
        )

    @staticmethod
    def store_item(item, trading_floor_id):
        with DBHelper.transaction_scope():
            arbitrator = DBHelper.store_and_get_arbitrator(item)
            organizer = DBHelper.store_and_get_organizer(item, arbitrator)
            debtor = DBHelper.store_and_get_debtor(item)
            auction = DBHelper.store_and_get_auction(
                item=item,
                organizer=organizer,
                arbitrator=arbitrator,
                debtor=debtor,
                trading_floor_id=trading_floor_id,
            )
            if case_number := item.get("case_number"):
                legal_case = DBHelper.store_legal_case_from_case_number(case_number)
                auction.legal_case_id = legal_case.id if legal_case else None
            lot = DBHelper.store_and_get_lot(item, auction.id)
            DBHelper.store_lot_period(item, lot.id)
            DBHelper.store_files(item, lot.id, auction.id)

    @staticmethod
    def store_and_get_auction(
            item: EtpItem,
            trading_floor_id: int,
            organizer: Counterparty | None = None,
            arbitrator: Counterparty | None = None,
            debtor: Counterparty | None = None,
    ):
        auction = (
            DBHelper.session.query(Auction)
            .filter_by(ext_id=item["trading_id"], trading_floor_id=trading_floor_id)
            .first()
        )
        if not auction:
            if parse_fedresurs and not all([organizer, arbitrator]):
                trading_floor_name = (
                    DBHelper.session.query(TradingFloor.name)
                    .filter_by(id=trading_floor_id)
                    .scalar()
                )
                auction_client = AuctionFedresurs(
                    trading_id=item["trading_id"],
                    trading_number=item["trading_number"],
                    case_number=item.get("case_number"),
                    trading_floor_name=trading_floor_name,
                )
                if auction_client.get_guid():
                    auction_client.parse_main_info()
                arbitrator = arbitrator or DBHelper.store_and_get_arbitrator(
                    auction_client.data
                )
                organizer = organizer or DBHelper.store_and_get_organizer(
                    item, arbitrator
                )
            property_type = item.get("property_type")
            if isinstance(property_type, AuctionPropertyType):
                property_type = property_type.value
            auction = Auction(
                ext_id=item["trading_id"],
                property_type=property_type,
                url=item["trading_link"],
                number=item.get("trading_number"),
                type=item.get("trading_type"),
                form=item.get("trading_form"),
                message_number=item.get("msg_number"),
                organizer_id=organizer.id if organizer else None,
                arbitrator_id=arbitrator.id if arbitrator else None,
                debtor_id=debtor.id if debtor else None,
                trading_floor_id=trading_floor_id,
            )
            DBHelper.session.add(auction)
            DBHelper.session.flush()

        return auction

    @staticmethod
    def get_or_create_address(address_str: str) -> Address | None:
        if not address_str:
            return None
        from app.utils.location import RegionIdentifier

        with DBHelper.transaction_scope():
            address = (
                DBHelper.session.query(Address).filter_by(name=address_str).first()
            )
            if not address:
                address = Address(name=address_str)
                region_name = RegionIdentifier.get_region(address_str)
                if region_name:
                    if (
                            region := DBHelper.session.query(Region)
                                    .filter_by(name=region_name)
                                    .first()
                    ):
                        address.region = region
                    else:
                        logger.warning(
                            f"Region oktmo with name {region_name} not found."
                        )
                DBHelper.session.add(address)
            return address

    @staticmethod
    def store_model(model_or_models: Base | list[Base]) -> Base:
        def _store_single_model(model: Base):
            logger.info(f"Storing model {model}")
            if isinstance(model, Counterparty):
                if session.query(Counterparty).filter_by(inn=model.inn).first():
                    return session.merge(model)
            elif isinstance(model, LegalCase):
                if session.query(LegalCase).filter_by(number=model.number).first():
                    return session.merge(model)
            elif isinstance(model, DebtorMessage):
                if session.query(DebtorMessage).filter_by(number=model.number).first():
                    return session.merge(model)
            elif isinstance(model, File):
                if session.query(File).filter_by(name=model.name).first():
                    return session.merge(model)
            session.add(model)
            return model

        with DBHelper.transaction_scope() as session:
            if isinstance(model_or_models, list):
                result = []
                for model in model_or_models:
                    result.append(_store_single_model(model))
                return result
            else:
                return _store_single_model(model_or_models)

    @staticmethod
    def store_and_get_arbitrator(item: EtpItem | dict):
        name = item.get("arbit_manager")
        if name and name == item.get("trading_org"):
            inn = item.get("trading_org_inn", item.get("arbit_manager_inn"))
        else:
            inn = item.get("arbit_manager_inn")
        arbitrator_counterparty = DBHelper.get_counterparty(
            inn=inn, name=name, short_name=name
        )
        if not arbitrator_counterparty:
            if parse_fedresurs and not arbitrator_counterparty.fedresurs_url:
                if inn := item.get("arbit_manager_inn"):
                    if len(inn) > 10:
                        arb_client = PersonFedresurs(inn, item.get("arbit_manager"))
                    else:
                        arb_client = CompanyFedresurs(inn, item.get("arbit_manager"))
                else:
                    amf = ArbitrManagerFedresurs(item.get("arbit_manager"))
                    arb_client = amf if amf.data.get("guid") else None
                if not arb_client:
                    pass
                elif not arb_client.data.get("guid"):
                    arbitrator_counterparty = arbitrator_counterparty or Counterparty(
                        inn=item.get("arbit_manager_inn"),
                        short_name=item.get("arbit_manager"),
                        type=arb_client.data.get("type"),
                    )
                    if inspect(arbitrator_counterparty).transient:
                        DBHelper.session.add(arbitrator_counterparty)
                        DBHelper.session.flush()
                else:
                    arb_client.parse()
                    if not (
                            arbitrator_counterparty := DBHelper.get_counterparty(
                                inn=arb_client.data.get("inn"),
                                name=arb_client.data.get("name"),
                                short_name=arb_client.data.get("short_name"),
                            )
                    ):
                        arb_client.parse_sro_membership()
                        arbitrator_counterparty = (
                            DBHelper.store_counterparty_and_co_from_dict(
                                arb_client.data
                            )
                        )
            elif any([inn, name]):
                arbitrator_counterparty = DBHelper.store_model(
                    Counterparty(inn=inn, name=name, short_name=name)
                )
                DBHelper.session.add(arbitrator_counterparty)
                DBHelper.session.flush()
                sro = None
                if arbit_manager_org := item.get("arbit_manager_org"):
                    arbit_manager_org = arbit_manager_org.split()
                    arbit_manager_org = " ".join(arbit_manager_org)
                    if len(arbit_manager_org) > 10:
                        sro = DBHelper.store_model(Counterparty(name=arbit_manager_org))
                if (
                        arbitrator_counterparty
                        and sro
                        and not DBHelper.get_counterparty_sro(
                    arbitrator_counterparty.id, sro.short_name
                )
                ):
                    sro_membership = CounterpartySRO(
                        counterparty_id=arbitrator_counterparty.id,
                        sro_id=sro.id,
                    )
                    DBHelper.session.add(sro_membership)
        return arbitrator_counterparty

    @staticmethod
    def store_and_get_organizer(item: EtpItem, arbitrator_counterparty: Counterparty):
        if (
                (
                        item.get("trading_org_inn")
                        and item.get("trading_org_inn") == item.get("arbit_manager_inn")
                )
                or (
                item.get("trading_org")
                and item.get("trading_org") == item.get("arbit_manager")
        )
                or (
                item.get("trading_org")
                and arbitrator_counterparty
                and item.get("trading_org") == arbitrator_counterparty.short_name
        )
                or (
                item.get("trading_org")
                and arbitrator_counterparty
                and item.get("trading_org_inn") == arbitrator_counterparty.inn
        )
        ):
            return arbitrator_counterparty
        organizer_counterparty: Counterparty = DBHelper.get_counterparty(
            inn=item.get("trading_org_inn"),
            name=item.get("trading_org"),
            short_name=item.get("trading_org"),
        )
        if not organizer_counterparty:
            if parse_fedresurs and not organizer_counterparty.fedresurs_url:
                if inn := item.get("trading_org_inn"):
                    if len(inn) > 10:
                        org_client = PersonFedresurs(inn, item["trading_org"])
                    else:
                        org_client = CompanyFedresurs(inn, item["trading_org"])
                else:
                    if guid := (
                            ArbitrManagerFedresurs(item.get("trading_org")).data.get("guid")
                            or PersonOrganizerFedresurs(item.get("trading_org")).data.get(
                        "guid"
                    )
                    ):
                        org_client = PersonFedresurs(
                            name=item.get("trading_org"), guid=guid
                        )
                    elif guid := CompanyOrganizerFedresurs(
                            item.get("trading_org")
                    ).data.get("guid"):
                        org_client = CompanyFedresurs(
                            name=item.get("trading_org"), guid=guid
                        )
                    else:
                        org_client = None
                if not org_client:
                    pass
                elif not org_client.data["guid"]:
                    organizer_counterparty = organizer_counterparty or Counterparty(
                        inn=item.get("trading_org_inn"),
                        short_name=item.get("trading_org"),
                        email=item.get("trading_org_contacts", {}).get("email"),
                        phone=item.get("trading_org_contacts", {}).get("phone"),
                        type=org_client.data["type"],
                    )
                    if inspect(organizer_counterparty).transient:
                        DBHelper.session.add(organizer_counterparty)
                        DBHelper.session.flush()
                else:
                    org_client.parse()
                    if not (
                            organizer_counterparty := DBHelper.get_counterparty(
                                inn=org_client.data.get("inn"),
                                name=org_client.data.get("name"),
                                short_name=org_client.data.get("short_name"),
                            )
                    ):
                        org_client.parse_sro_membership()
                        organizer_counterparty = (
                            DBHelper.store_counterparty_and_co_from_dict(
                                org_client.data
                            )
                        )
            elif any([item.get("trading_org_inn"), item.get("trading_org")]):
                organizer_counterparty = DBHelper.store_model(
                    Counterparty(
                        inn=item.get("trading_org_inn"),
                        name=item.get("trading_org"),
                        short_name=item.get("trading_org"),
                    )
                )
                DBHelper.session.add(organizer_counterparty)
                DBHelper.session.flush()
        return organizer_counterparty

    @staticmethod
    def store_and_get_debtor(item: EtpItem | dict):
        debtor_counterparty = DBHelper.get_counterparty(inn=item["debtor_inn"])
        if not debtor_counterparty:
            if parse_fedresurs and not debtor_counterparty.fedresurs_url:
                if inn := item["debtor_inn"]:
                    debtor_client = (
                        PersonFedresurs(inn=inn)
                        if len(inn) > 10
                        else CompanyFedresurs(inn=inn)
                    )
                else:
                    debtor_client = None
                    if guid := CounterpartyFedresurs(inn=inn).data.get("guid"):
                        debtor_client = PersonFedresurs(inn=inn, guid=guid)
                    elif guid := CompanyFedresurs(inn=inn).data.get("guid"):
                        debtor_client = CompanyFedresurs(inn=inn, guid=guid)
                if not debtor_client:
                    pass
                elif not debtor_client.data["guid"]:
                    address = DBHelper.get_or_create_address(item["address"])
                    debtor_counterparty = debtor_counterparty or Counterparty(
                        inn=item["debtor_inn"],
                        address_id=address.id if address else None,
                        type=debtor_client.data["type"],
                    )
                    if inspect(debtor_counterparty).transient:
                        DBHelper.session.add(debtor_counterparty)
                        DBHelper.session.flush()
                else:
                    debtor_client.parse()
                    if not (
                            debtor_counterparty := DBHelper.get_counterparty(
                                inn=debtor_client.data.get("inn"),
                                name=debtor_client.data.get("name"),
                                short_name=debtor_client.data.get("short_name"),
                            )
                    ):
                        debtor_client.parse_sro_membership()
                        debtor_client.parse_bankruptcy()
                        debtor_client.parse_publications()
                        debtor_client.data["address"] = (
                                debtor_client.data["address"] or item["address"]
                        )
                        debtor_counterparty = (
                            DBHelper.store_counterparty_and_co_from_dict(
                                debtor_client.data
                            )
                        )
            elif debtor_inn := item.get("debtor_inn"):
                debtor_counterparty = DBHelper.store_model(
                    Counterparty(
                        inn=debtor_inn,
                    )
                )
                DBHelper.session.add(debtor_counterparty)
                DBHelper.session.flush()
        return debtor_counterparty

    @staticmethod
    def store_counterparty_and_co_from_dict(data: dict) -> Counterparty:
        counterparty = DBHelper.store_counterparty_from_dict(data)
        if not counterparty.sro_memberships:
            for membership in data.get("sro_memberships", []):
                sro = DBHelper.store_counterparty_from_dict(membership)
                if not DBHelper.get_counterparty_sro(counterparty.id, sro.short_name):
                    sro_membership = CounterpartySRO(
                        counterparty_id=counterparty.id,
                        sro_id=sro.id,
                        message_number=membership["message_number"],
                        activity_type=membership["activity_type"],
                        entered_at=membership["entered_at"],
                    )
                    DBHelper.session.add(sro_membership)
        for legal_case_data in data.get("legal_cases", []):
            DBHelper.store_legal_case_from_dict(legal_case_data)
        for message in data.get("publications", []):
            DBHelper.store_debtor_message_from_dict(message, counterparty)
        return counterparty

    @staticmethod
    def store_counterparty_from_dict(data: dict) -> Counterparty:
        address = DBHelper.get_or_create_address(data.get("address"))
        counterparty = Counterparty(
            inn=data["inn"],
            kpp=data.get("kpp"),
            snils=data.get("snils"),
            ogrn=data.get("ogrn"),
            ogrnip=data.get("ogrnip"),
            okopf=data.get("okopf"),
            name=data["name"],
            short_name=data.get("short_name"),
            email=data["email"],
            phone=data["phone"],
            url=data["url"],
            fedresurs_url=data.get("fedresurs_url"),
            type=data["type"],
            address_id=address.id if address else None,
        )
        existing_counterparty = (
            DBHelper.session.query(Counterparty).filter_by(inn=counterparty.inn).first()
        )
        if existing_counterparty:
            if not existing_counterparty.fedresurs_url:
                for field in [
                    "kpp",
                    "snils",
                    "ogrn",
                    "ogrnip",
                    "okopf",
                    "name",
                    "short_name",
                    "email",
                    "phone",
                    "url",
                    "fedresurs_url",
                    "type",
                    "address_id",
                ]:
                    setattr(existing_counterparty, field, getattr(counterparty, field))
                counterparty = existing_counterparty
            else:
                return existing_counterparty
        else:
            DBHelper.session.add(counterparty)
            DBHelper.session.flush()
        return counterparty

    @staticmethod
    def store_legal_case_from_dict(data: dict) -> LegalCase:
        if not (
                legal_case := DBHelper.session.query(LegalCase)
                        .filter_by(number=data["number"])
                        .first()
        ):
            legal_case = LegalCase(
                number=data["number"],
                court_name=data.get("court_name"),
                fedresurs_url=data.get("fedresurs_url"),
                status=data.get("status"),
                debtor_category=data.get("debtor_category"),
            )
            DBHelper.session.add(legal_case)
            DBHelper.session.flush()
        return legal_case

    @staticmethod
    def store_debtor_message_from_dict(
            data: dict, debtor: Counterparty
    ) -> DebtorMessage:
        if not (
                debtor_message := DBHelper.session.query(DebtorMessage)
                        .filter_by(number=data["number"])
                        .first()
        ):
            legal_case = (
                DBHelper.session.query(LegalCase)
                .filter_by(number=data["legal_case_number"])
                .first()
            )
            if not legal_case:
                pass
            debtor_message = DebtorMessage(
                number=data.get("number"),
                type=data["type"],
                content=data.get("content"),
                fedresurs_url=data["fedresurs_url"],
                published_at=data["published_at"],
                debtor_id=debtor.id,
                legal_case_id=legal_case.id if legal_case else None,
            )
            DBHelper.session.add(debtor_message)
            DBHelper.session.flush()
            DBHelper.download_files(
                debtor_message.id,
                DebtorMessage,
                [
                    DownloadData(
                        url=file["url"],
                        file_name=file["name"],
                        referer=data["fedresurs_url"],
                    )
                    for file in data.get("files")
                ],
            )
        return debtor_message

    @staticmethod
    def store_legal_case_from_case_number(case_number: str) -> Optional[LegalCase]:
        from app.utils.fedresurs import LegalCaseFedresurs

        if not case_number:
            return None

        legal_case = DBHelper.session.execute(
            select(LegalCase).where(LegalCase.number.like(f"%{case_number}%"))
        ).scalar()
        if not legal_case:
            if parse_fedresurs:
                fed_client = LegalCaseFedresurs(case_number)
                fed_client.parse()
                legal_case_data = fed_client.data
                legal_case = DBHelper.store_legal_case_from_dict(legal_case_data)
            else:
                legal_case = DBHelper.store_model(
                    LegalCase(
                        number=case_number,
                    )
                )
        return legal_case

    @staticmethod
    def store_and_get_lot(item: EtpItem, auction_id: int):
        lot = (
            DBHelper.session.query(Lot)
            .filter_by(auction_id=auction_id, number=item["lot_number"])
            .first()
        )
        if not lot:
            lot = Lot(
                ext_id=item["lot_id"],
                url=item["lot_link"],
                number=item.get("lot_number"),
                name=item.get("short_name"),
                info=item.get("lot_info"),
                price_step=item.get("step_price"),
                price_start=item.get("start_price"),
                property_info=item.get("property_information"),
                auction_id=auction_id,
            )
            DBHelper.session.add(lot)
            DBHelper.session.flush()

            if categories := item.get("categories"):
                categories = parse_classifiers(categories)
                for code in categories:
                    lot_category = LotCategory(code=code, lot_id=lot.id)
                    DBHelper.session.add(lot_category)
        return lot

    @staticmethod
    def store_lot_period(item: EtpItem, lot_id: int):
        def add_period(period: dict):
            lot_period = LotPeriod(
                request_start_at=period["start_date_requests"],
                request_end_at=period["end_date_requests"],
                trading_start_at=period.get("start_date_trading")
                                 or period.get("start_date_requests"),
                trading_end_at=period["end_date_trading"],
                price=period["current_price"],
                lot_id=lot_id,
            )
            DBHelper.session.add(lot_period)

        lot_period = DBHelper.session.query(LotPeriod).filter_by(lot_id=lot_id).first()
        if not lot_period:
            if periods := item["periods"]:
                for period in periods:
                    add_period(period)
            else:
                if item["start_date_requests"]:
                    add_period(
                        dict(
                            start_date_requests=item["start_date_requests"],
                            end_date_requests=item["end_date_requests"],
                            start_date_trading=item["start_date_trading"],
                            end_date_trading=item["end_date_trading"],
                            current_price=item["step_price"] or 0,
                        )
                    )

    @staticmethod
    def store_files(item: EtpItem, lot_id: int, auction_id: int):
        files = item.get("files", {})
        if not files:
            return
        general_files_download_data: list[DownloadData] = files.get("general")
        if general_files_download_data:
            DBHelper.download_files(auction_id, Auction, general_files_download_data)

        if not (lot_files_download_data := files.get("lot")):
            return
        DBHelper.download_files(lot_id, Lot, lot_files_download_data)

    @staticmethod
    def download_files(
            model_id: int,
            model: Type[Auction | Lot | LegalCase | DebtorMessage],
            download_datas: list[DownloadData],
    ):
        model_type = {
            Auction: FileModelType.Auction,
            Lot: FileModelType.Lot,
            LegalCase: FileModelType.LegalCase,
            DebtorMessage: FileModelType.DebtorMessage,
        }[model]
        model_lowercase = {
            Auction: "auction",
            Lot: "lot",
            LegalCase: "legal_case",
            DebtorMessage: "debtor_message",
        }[model]
        existing_files = (
            DBHelper.session.query(File)
            .filter_by(model_type=model_type, model_id=model_id)
            .all()
        )
        existing_file_names = {file.name for file in existing_files}
        absolute_download_dir_path = (
                absolute_download_path / f"{model_lowercase}_{model_id}"
        )
        relative_download_dir_path = (
                relative_download_path / f"{model_lowercase}_{model_id}"
        )
        file_objs = list()
        for download_data in download_datas:
            file_name = sanitize_filename(download_data.file_name)
            if len(file_name) > 75:
                file_name = file_name[:30] + "_" + file_name[-35::1]
            if file_name in existing_file_names:
                continue
            absolute_path = absolute_download_dir_path / file_name
            relative_path = relative_download_dir_path / file_name
            if absolute_path.suffix.lower() not in allowable_formats:
                continue
            if download_data.method == "GET" and not download_files_from_get_url:
                paths = [None]
            else:
                Path(absolute_download_dir_path).mkdir(parents=True, exist_ok=True)
                paths = DownloadFiles.request_to_download_general(
                    download_data=download_data,
                    absolute_path=absolute_path,
                    relative_path=relative_path,
                )
            # paths может быть списком из более чем одного элемента в случае если архив в download_data
            for path in paths:  # type: pathlib.Path
                is_image = download_data.is_image or (path.suffix.lower() in image_formats if path else False)
                file_objs.append(
                    File(
                        name=path.name if path else file_name,
                        path=path.as_posix() if path else None,
                        url=str(download_data.url)
                        if download_data.method == "GET"
                        else None,
                        model_type=model_type,
                        model_id=model_id,
                        is_image=is_image,
                        is_image_from_archive=is_image and absolute_path.suffix.lower() in archive_formats,
                        order=download_data.order,
                    )
                )
        DBHelper.session.add_all(file_objs)


if __name__ == "__main__":
    DBHelper.create_new_connection()
    DBHelper.add_regions()
    DBHelper.add_cities()
    DBHelper.add_addresses()
    DBHelper.add_trading_floors()
