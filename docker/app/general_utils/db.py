import csv
import logging
import pathlib
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import PurePath, Path

from sqlalchemy import create_engine, text, select, and_, or_, inspect, literal
from sqlalchemy.orm import sessionmaker, joinedload, aliased
from typing import Type, Union, List

from general_utils import EtpItem, parse_classifiers
from general_utils.config import (
    data_path, absolute_download_path, relative_download_path, download_files_from_get_url, allowable_formats
)
from general_utils.download import DownloadFiles
from general_utils.models import (
    Auction, ParserStatus, TradingFloor, Address, Region, City, Counterparty, Lot, LotPeriod, File, LegalCase, Base,
    DebtorMessage, DownloadData
)
from general_utils.fedresurs import (
    PersonFedresurs, CompanyFedresurs, ArbitrManagerFedresurs, CounterpartyFedresurs, PersonOrganizerFedresurs,
    CompanyOrganizerFedresurs, AuctionFedresurs
)
from general_utils.models.counterparty import CounterpartySRO
from general_utils.models.file import FileModelType
from general_utils.models.lot import LotCategory
from general_utils.models.parser_status import StatusType
from general_utils.python_mysql_dbconfig import read_db_config
from general_utils.work_with_path_and_dir import sanitize_filename

logger = logging.getLogger(__name__)
db_config = read_db_config()
connection_string = f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}'

engine = create_engine(connection_string, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    DBHelper.set_wait_timeout(db)
    return db


class DBHelper:

    @staticmethod
    @contextmanager
    def transaction_scope(existing_session: SessionLocal = None, commit: bool = True, flush: bool = False):
        if existing_session:
            yield existing_session
            if commit:
                existing_session.commit()
            return
        session = SessionLocal()
        DBHelper.set_wait_timeout(session)
        try:
            yield session
            if commit:
                session.commit()
            elif flush:
                session.flush()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction failed: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def set_wait_timeout(session: SessionLocal, timeout: int = 600):
        session.execute(text(f"SET SESSION wait_timeout = {timeout};"))
        # logger.info(f"Session wait_timeout set to {timeout} seconds.")

    @staticmethod
    def get_latest_lot(data_origin_url: str, keys=None, day: int = 30) -> Union[tuple[List, int], None]:
        date_threshold = datetime.utcnow() - timedelta(days=day)
        if keys is None:
            keys = [Auction.url]
        if not isinstance(keys, list):
            keys = [keys]

        with DBHelper.transaction_scope(commit=False) as session:
            trading_floor_id = session.scalars(
                select(TradingFloor.id).where(TradingFloor.url == literal(data_origin_url))
            ).first()
            if trading_floor_id is None:
                return

            stmt = select(*keys).where(
                and_(Auction.created_at >= date_threshold, Auction.trading_floor_id == trading_floor_id)
            )
            lots = session.scalars(stmt).all()
            return lots, trading_floor_id

    @staticmethod
    def get_trading_floor_id(session: SessionLocal, crawler_name: str, data_origin_url: str):
        with DBHelper.transaction_scope(session) as session:
            trading_floor_id = session.scalars(
                select(TradingFloor.id).where(TradingFloor.url == literal(data_origin_url))
            ).first()
            if trading_floor_id is None:
                logger.error(f"get_latest_lot :: TradingFloor not found for URL {data_origin_url}. Skipping.")
                return None

            new_parser_status = ParserStatus(name=crawler_name, trading_floor_id=trading_floor_id)
            session.add(new_parser_status)
        return trading_floor_id

    @staticmethod
    def save_counter_and_duration(
            counter: int, duration: float, status_active: bool, spider_name: str, trading_floor_id: int
    ):
        if status_active is not None:
            with DBHelper.transaction_scope() as session:
                status = StatusType.active if status_active else StatusType.disabled
                session.add(ParserStatus(
                    name=spider_name,
                    trading_floor_id=trading_floor_id,
                    counter=counter,
                    duration=duration,
                    status=status
                ))
                trading_floor = session.query(TradingFloor).filter_by(id=trading_floor_id).first()
                if trading_floor.status != status:
                    trading_floor.status = StatusType.active if status_active else StatusType.disabled
                logger.info(
                    f"save_counter_and_duration :: "
                    f"Updated counter and duration for '{spider_name}' to {counter}, {duration}."
                )

    @staticmethod
    def add_regions():
        regions = []
        with open(data_path / 'regions_with_oktmo.csv', newline='', encoding='utf-8') as csvfile:
            reader: csv.DictReader = csv.DictReader(csvfile, delimiter=':')
            for row in reader:
                regions.append(Region(oktmo=int(row['oktmo']), name=row['region']))

        with DBHelper.transaction_scope() as session:
            session.add_all(regions)

    @staticmethod
    def add_addresses(source_path: PurePath = data_path / 'addresses.csv', addresses: list[Address] = None):
        addresses = addresses or []
        regions = DBHelper.get_regions_dict()
        if not addresses:
            with open(source_path, newline='', encoding='utf-8') as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if id_ := regions.get(row['region']):
                        addresses.append(Address(region_id=id_, name=row['address']))
                    else:
                        pass
        with DBHelper.transaction_scope() as session:
            session.add_all(addresses)

    @staticmethod
    def add_cities(source_path: PurePath = data_path / 'cities.csv', cities: list[City] = None):
        cities = cities or []
        regions = DBHelper.get_regions_dict()
        if not cities:
            with open(source_path, newline='', encoding='utf-8') as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if id_ := regions.get(row['region']):
                        cities.append(City(region_id=id_, name=row['city']))
                    else:
                        pass
        with DBHelper.transaction_scope() as session:
            session.add_all(cities)

    @staticmethod
    def add_trading_floors(
            source_path: PurePath = data_path / 'trading_floors.csv', trading_floors: list[TradingFloor] = None
    ):
        trading_floors = trading_floors or []
        if not trading_floors:
            with open(source_path, newline='', encoding='utf-8') as csvfile:
                reader: csv.DictReader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    trading_floors.append(TradingFloor(name=row['name'], url=row['url']))
        with DBHelper.transaction_scope() as session:
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
    def get_region_names():
        with DBHelper.transaction_scope(commit=False) as session:
            return session.scalars(select(Region.name)).all()

    @staticmethod
    def get_cities_with_regions():
        with DBHelper.transaction_scope(commit=False) as session:
            return session.query(City).options(joinedload(City.region)).all()

    @staticmethod
    def get_all(model: Type[Base]):
        with DBHelper.transaction_scope(commit=False) as session:
            query = session.query(model)
            if model is TradingFloor:
                query = query.options(joinedload(TradingFloor.counterparty).joinedload(Counterparty.sro_memberships))
            elif model is LegalCase:
                query = query.options(joinedload(LegalCase.auctions).joinedload(Auction.debtor))
            elif model is Counterparty:
                query = query.options(joinedload(Counterparty.sro_memberships))
            elif model is Auction:
                query = query.options(
                    joinedload(Auction.trading_floor),
                    joinedload(Auction.legal_case)
                )
            return query.all()

    @staticmethod
    def get_regions_dict():
        with DBHelper.transaction_scope(commit=False) as session:
            return {region.file_name: region.id for region in session.query(Region).all()}

    @staticmethod
    def get_counterparty(session: SessionLocal = None, inn: str = None, name: str = None, short_name: str = None):
        with DBHelper.transaction_scope(session, commit=False) as session:
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
    def get_counterparty_sro(counterparty_id: int, sro_counterparty_short_name: str, session: SessionLocal):
        sro_alias = aliased(Counterparty)
        return (
            session.query(CounterpartySRO)
            .join(Counterparty, Counterparty.id == CounterpartySRO.counterparty_id)
            .join(sro_alias, sro_alias.id == CounterpartySRO.sro_id)
            .filter(and_(
                CounterpartySRO.counterparty_id == counterparty_id,
                sro_alias.short_name == sro_counterparty_short_name
            )).first()
        )

    @staticmethod
    def store_item(item, trading_floor_id, session=None):
        with DBHelper.transaction_scope(session):
            arbitrator = DBHelper.store_and_get_arbitrator(item, session)
            organizer = DBHelper.store_and_get_organizer(item, arbitrator, session)
            debtor = DBHelper.store_and_get_debtor(item, session)
            auction = DBHelper.store_and_get_auction(
                item=item, organizer=organizer, arbitrator=arbitrator, debtor=debtor,
                trading_floor_id=trading_floor_id, session=session
            )
            if case_number := item['case_number']:
                legal_case = DBHelper.store_legal_case_from_case_number(case_number, session)
                auction.legal_case_id = legal_case.id
            lot = DBHelper.store_and_get_lot(item, auction.id, session)
            DBHelper.store_lot_period(item, lot.id, session)
            DBHelper.store_files(item, lot.id, auction.id, session)

    @staticmethod
    def store_and_get_auction(
            item: EtpItem, trading_floor_id: int, session: SessionLocal,
            organizer: Counterparty = None, arbitrator: Counterparty = None, debtor: Counterparty = None
    ):
        auction = session.query(Auction).filter_by(ext_id=item['trading_id'], trading_floor_id=trading_floor_id).first()
        if not auction:
            if not all([organizer, arbitrator]):
                trading_floor_name = session.query(TradingFloor.name).filter_by(id=trading_floor_id).scalar()
                auction_client = AuctionFedresurs(
                    trading_id=item['trading_id'], trading_number=item['trading_number'],
                    case_number=item['case_number'], trading_floor_name=trading_floor_name
                )
                if auction_client.get_guid():
                    auction_client.parse_main_info()
                arbitrator = arbitrator or DBHelper.store_and_get_arbitrator(auction_client.data, session)
                organizer = organizer or DBHelper.store_and_get_organizer(item, arbitrator, session)
            auction = Auction(
                ext_id=item['trading_id'],
                url=item['trading_link'],
                number=item.get('trading_number'),
                type=item.get('trading_type'),
                form=item.get('trading_form'),
                message_number=item.get('msg_number'),
                organizer_id=organizer.id if organizer else None,
                arbitrator_id=arbitrator.id if arbitrator else None,
                debtor_id=debtor.id if debtor else None,
                trading_floor_id=trading_floor_id,
            )
            session.add(auction)
            session.flush()
        return auction

    @staticmethod
    def get_or_create_address(address_str: str, session: SessionLocal) -> Address | None:
        if not address_str:
            return
        from general_utils.location import RegionIdentifier
        with DBHelper.transaction_scope(session) as session:
            address = session.query(Address).filter_by(name=address_str).first()
            if not address:
                address = Address(name=address_str)
                region_name = RegionIdentifier.get_region(address_str)
                if region_name:
                    if region := session.query(Region).filter_by(name=region_name).first():
                        address.region = region
                    else:
                        logger.warning(f"Region oktmo with name {region_name} not found.")
                session.add(address)
            return address

    @staticmethod
    def store_model(model_or_models: Base | list[Base]):
        def _store_single_model(model: Base):
            logger.info(f'Storing model {model}')
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
    def store_and_get_arbitrator(item: EtpItem | dict, session: SessionLocal):
        name = item.get('arbit_manager')
        if name and name == item.get('trading_org'):
            inn = item.get('trading_org_inn', item.get('arbit_manager_inn'))
        else:
            inn = item.get('arbit_manager_inn')
        arbitrator_counterparty = DBHelper.get_counterparty(inn=inn, name=name, short_name=name)
        if not arbitrator_counterparty or not arbitrator_counterparty.fedresurs_url:
            if inn := item.get('arbit_manager_inn'):
                if len(inn) > 10:
                    arb_client = PersonFedresurs(inn, item.get('arbit_manager'))
                else:
                    arb_client = CompanyFedresurs(inn, item.get('arbit_manager'))
            else:
                amf = ArbitrManagerFedresurs(item.get('arbit_manager'))
                arb_client = amf if amf.data.get('guid') else None
            if not arb_client:
                pass
            elif not arb_client.data.get('guid'):
                arbitrator_counterparty = arbitrator_counterparty or Counterparty(
                    inn=item.get('arbit_manager_inn'),
                    short_name=item.get('arbit_manager'),
                    type=arb_client.data.get('type')
                )
                if inspect(arbitrator_counterparty).transient:
                    session.add(arbitrator_counterparty)
                    session.flush()
            else:
                arb_client.parse()
                if not (arbitrator_counterparty := DBHelper.get_counterparty(
                        inn=arb_client.data.get('inn'),
                        name=arb_client.data.get('name'),
                        short_name=arb_client.data.get('short_name')
                )):
                    arb_client.parse_sro_membership()
                    arbitrator_counterparty = DBHelper.store_counterparty_and_co_from_dict(arb_client.data, session)
        return arbitrator_counterparty

    @staticmethod
    def store_and_get_organizer(item: EtpItem, arbitrator_counterparty: Counterparty, session: SessionLocal):
        if (
                (item.get('trading_org_inn') and item.get('trading_org_inn') == item.get('arbit_manager_inn')) or
                (item.get('trading_org') and item.get('trading_org') == item.get('arbit_manager')) or
                (
                        item.get('trading_org') and arbitrator_counterparty and
                        item.get('trading_org') == arbitrator_counterparty.short_name
                ) or
                (
                        item.get('trading_org') and arbitrator_counterparty and
                        item.get('trading_org_inn') == arbitrator_counterparty.inn
                )
        ):
            return arbitrator_counterparty
        organizer_counterparty: Counterparty = DBHelper.get_counterparty(
            inn=item.get('trading_org_inn'),
            name=item.get('trading_org'),
            short_name=item.get('trading_org')
        )
        if not organizer_counterparty or not organizer_counterparty.fedresurs_url:
            if inn := item.get('trading_org_inn'):
                if len(inn) > 10:
                    org_client = PersonFedresurs(inn, item['trading_org'])
                else:
                    org_client = CompanyFedresurs(inn, item['trading_org'])
            else:
                if guid := (
                        ArbitrManagerFedresurs(item.get('trading_org')).data.get('guid') or
                        PersonOrganizerFedresurs(item.get('trading_org')).data.get('guid')
                ):
                    org_client = PersonFedresurs(name=item.get('trading_org'), guid=guid)
                elif guid := CompanyOrganizerFedresurs(item.get('trading_org')).data.get('guid'):
                    org_client = CompanyFedresurs(name=item.get('trading_org'), guid=guid)
                else:
                    org_client = None
            if not org_client:
                pass
            elif not org_client.data['guid']:
                organizer_counterparty = organizer_counterparty or Counterparty(
                    inn=item.get('trading_org_inn'),
                    short_name=item.get('trading_org'),
                    email=item.get('trading_org_contacts', {}).get('email'),
                    phone=item.get('trading_org_contacts', {}).get('phone'),
                    type=org_client.data['type']
                )
                if inspect(organizer_counterparty).transient:
                    session.add(organizer_counterparty)
                    session.flush()
            else:
                org_client.parse()
                if not (organizer_counterparty := DBHelper.get_counterparty(
                        inn=org_client.data.get('inn'),
                        name=org_client.data.get('name'),
                        short_name=org_client.data.get('short_name')
                )):
                    org_client.parse_sro_membership()
                    organizer_counterparty = DBHelper.store_counterparty_and_co_from_dict(org_client.data, session)
        return organizer_counterparty

    @staticmethod
    def store_and_get_debtor(item: EtpItem | dict, session: SessionLocal):
        debtor_counterparty = DBHelper.get_counterparty(inn=item['debtor_inn'])
        if not debtor_counterparty or not debtor_counterparty.fedresurs_url:
            if inn := item['debtor_inn']:
                debtor_client = PersonFedresurs(inn=inn) if len(inn) > 10 else CompanyFedresurs(inn=inn)
            else:
                debtor_client = None
                if guid := CounterpartyFedresurs(inn=inn).data.get('guid'):
                    debtor_client = PersonFedresurs(inn=inn, guid=guid)
                elif guid := CompanyFedresurs(inn=inn).data.get('guid'):
                    debtor_client = CompanyFedresurs(inn=inn, guid=guid)
            if not debtor_client:
                pass
            elif not debtor_client.data['guid']:
                address = DBHelper.get_or_create_address(item['address'], session)
                debtor_counterparty = debtor_counterparty or Counterparty(
                    inn=item['debtor_inn'], address_id=address.id if address else None,
                    type=debtor_client.data['type']
                )
                if inspect(debtor_counterparty).transient:
                    session.add(debtor_counterparty)
                    session.flush()
            else:
                debtor_client.parse()
                if not (debtor_counterparty := DBHelper.get_counterparty(
                        inn=debtor_client.data.get('inn'),
                        name=debtor_client.data.get('name'),
                        short_name=debtor_client.data.get('short_name')
                )):
                    debtor_client.parse_sro_membership()
                    debtor_client.parse_bankruptcy()
                    debtor_client.parse_publications()
                    debtor_client.data['address'] = debtor_client.data['address'] or item['address']
                    debtor_counterparty = DBHelper.store_counterparty_and_co_from_dict(debtor_client.data, session)
        return debtor_counterparty

    @staticmethod
    def store_counterparty_and_co_from_dict(data: dict, session: SessionLocal) -> Counterparty:
        counterparty = DBHelper.store_counterparty_from_dict(data, session)
        if not counterparty.sro_memberships:
            for membership in data.get('sro_memberships', []):
                sro = DBHelper.store_counterparty_from_dict(membership, session)
                if not DBHelper.get_counterparty_sro(counterparty.id, sro.short_name, session):
                    sro_membership = CounterpartySRO(
                        counterparty_id=counterparty.id,
                        sro_id=sro.id,
                        message_number=membership['message_number'],
                        activity_type=membership['activity_type'],
                        entered_at=membership['entered_at']
                    )
                    session.add(sro_membership)
        for legal_case_data in data.get('legal_cases', []):
            DBHelper.store_legal_case_from_dict(legal_case_data, session)
        for message in data.get('publications', []):
            DBHelper.store_debtor_message_from_dict(message, counterparty, session)
        return counterparty

    @staticmethod
    def store_counterparty_from_dict(data: dict, session: SessionLocal) -> Counterparty:
        address = DBHelper.get_or_create_address(data.get('address'), session)
        counterparty = Counterparty(
            inn=data['inn'],
            kpp=data.get('kpp'),
            snils=data.get('snils'),
            ogrn=data.get('ogrn'),
            ogrnip=data.get('ogrnip'),
            okopf=data.get('okopf'),
            name=data['name'],
            short_name=data.get('short_name'),
            email=data['email'],
            phone=data['phone'],
            url=data['url'],
            fedresurs_url=data.get('fedresurs_url'),
            type=data['type'],
            address_id=address.id if address else None
        )
        existing_counterparty = session.query(Counterparty).filter_by(inn=counterparty.inn).first()
        if existing_counterparty:
            if not existing_counterparty.fedresurs_url:
                for field in [
                    'kpp', 'snils', 'ogrn', 'ogrnip', 'okopf',
                    'name', 'short_name', 'email', 'phone', 'url',
                    'fedresurs_url', 'type', 'address_id'
                ]:
                    setattr(existing_counterparty, field, getattr(counterparty, field))
                counterparty = existing_counterparty
            else:
                return existing_counterparty
        else:
            session.add(counterparty)
            session.flush()
        return counterparty

    # @staticmethod
    # def store_legal_cases_and_messages_with_files_from_dict(
    #         legal_case_and_messages: dict, debtor_id: int, session: SessionLocal
    # ):
    #     legal_case_data = legal_case_and_messages['case']
    #     if legal_case_debtor_category := legal_case_data.get('debtor_category'):
    #         if not (debtor_category_id := DBHelper.get_debtor_category_id(legal_case_debtor_category, session)):
    #             new_debtor_category = DebtorCategory(name=legal_case_debtor_category)
    #             session.add(new_debtor_category)
    #             session.flush()
    #             debtor_category_id = new_debtor_category.id
    #         if not DBHelper.get_counterparty_debtor_category(debtor_id, debtor_category_id, session):
    #             session.add(
    #                 CounterpartyDebtorCategory(counterparty_id=debtor_id, debtor_category_id=debtor_category_id)
    #             )
    #     if not (legal_case := DBHelper.store_legal_case_from_dict(legal_case_data, session)):
    #         legal_case = DBHelper.store_legal_case_from_dict(legal_case_data, session)
    #     messages_and_files = legal_case_and_messages['messages']
    #     for message_and_files in messages_and_files:
    #         message = message_and_files['message']
    #         files = message_and_files['files']
    #         debtor_message = DBHelper.store_debtor_message_from_dict(message, legal_case.id, session)
    #         for file in files:
    #             file.model_id = debtor_message.id
    #         session.add_all(files)

    @staticmethod
    def store_legal_case_from_dict(data: dict, session: SessionLocal) -> LegalCase:
        if not (legal_case := session.query(LegalCase).filter_by(number=data['number']).first()):
            legal_case = LegalCase(
                number=data['number'],
                court_name=data.get('court_name'),
                fedresurs_url=data.get('fedresurs_url'),
                status=data.get('status'),
                debtor_category=data.get('debtor_category')
            )
            session.add(legal_case)
            session.flush()
        return legal_case

    @staticmethod
    def store_debtor_message_from_dict(data: dict, debtor: Counterparty, session: SessionLocal) -> DebtorMessage:
        if not (debtor_message := session.query(DebtorMessage).filter_by(number=data['number']).first()):
            legal_case = session.query(LegalCase).filter_by(number=data['legal_case_number']).first()
            if not legal_case:
                pass
            debtor_message = DebtorMessage(
                number=data.get('number'),
                type=data['type'],
                content=data.get('content'),
                fedresurs_url=data['fedresurs_url'],
                published_at=data['published_at'],
                debtor_id=debtor.id,
                legal_case_id=legal_case.id if legal_case else None
            )
            session.add(debtor_message)
            session.flush()
            DBHelper.download_files(session, debtor_message.id, DebtorMessage, [
                DownloadData(url=file['url'], file_name=file['name'], referer=data['fedresurs_url'])
                for file in data.get('files')
            ])
        return debtor_message

    @staticmethod
    def store_legal_case_from_case_number(case_number: str, session: SessionLocal) -> LegalCase:
        from general_utils.fedresurs import LegalCaseFedresurs
        legal_case = session.execute(select(LegalCase).where(LegalCase.number.like(f'%{case_number}%'))).scalar()
        if not legal_case:
            fed_client = LegalCaseFedresurs(case_number)
            fed_client.parse()
            legal_case_data = fed_client.data
            return DBHelper.store_legal_case_from_dict(legal_case_data, session)
        return legal_case

    @staticmethod
    def store_and_get_lot(item: EtpItem, auction_id: int, session: SessionLocal):
        lot = session.query(Lot).filter_by(auction_id=auction_id, number=item['lot_number']).first()
        if not lot:
            lot = Lot(
                ext_id=item['lot_id'],
                url=item['lot_link'],
                number=item.get('lot_number'),
                name=item.get('short_name'),
                info=item.get('lot_info'),
                price_step=item.get('step_price'),
                price_start=item.get('start_price'),
                property_info=item.get('property_information'),
                auction_id=auction_id
            )
            session.add(lot)
            session.flush()

            if categories := item.get('categories'):
                categories = parse_classifiers(categories)
                for code in categories:
                    lot_category = LotCategory(code=code, lot_id=lot.id)
                    session.add(lot_category)
        return lot

    @staticmethod
    def store_lot_period(item: EtpItem, lot_id: int, session: SessionLocal):
        def add_period(period: dict):
            lot_period = LotPeriod(
                request_start_at=period['start_date_requests'],
                request_end_at=period['end_date_requests'],
                trading_start_at=period['start_date_requests'],
                trading_end_at=period['end_date_trading'],
                price=period['current_price'],
                lot_id=lot_id,
            )
            session.add(lot_period)

        lot_period = session.query(LotPeriod).filter_by(lot_id=lot_id).first()
        if not lot_period:
            if periods := item['periods']:
                for period in periods:
                    add_period(period)
            else:
                if item['start_date_requests']:
                    add_period(dict(
                        start_date_requests=item['start_date_requests'],
                        end_date_requests=item['end_date_requests'],
                        start_date_trading=item['start_date_trading'],
                        end_date_trading=item['end_date_trading'],
                        current_price=item['step_price'] or 0,
                    ))

    @staticmethod
    def store_files(item: EtpItem, lot_id: int, auction_id: int, session: SessionLocal):
        files = item.get('files', {})
        if not files:
            return
        general_files_download_data: list[DownloadData] = files.get('general')
        if general_files_download_data:
            DBHelper.download_files(session, auction_id, Auction, general_files_download_data)

        if not (lot_files_download_data := files.get('lot')):
            return
        DBHelper.download_files(session, lot_id, Lot, lot_files_download_data)

    @staticmethod
    def download_files(
            session: SessionLocal, model_id: int, model: Type[Auction | Lot | LegalCase | DebtorMessage],
            download_datas: list[DownloadData]
    ):
        model_type = {
            Auction: FileModelType.Auction, Lot: FileModelType.Lot, LegalCase: FileModelType.LegalCase,
            DebtorMessage: FileModelType.DebtorMessage
        }[model]
        model_lowercase = {
            Auction: 'auction', Lot: 'lot', LegalCase: 'legal_case', DebtorMessage: 'debtor_message'
        }[model]
        existing_files = session.query(File).filter_by(model_type=model_type, model_id=model_id).all()
        existing_file_names = {file.name for file in existing_files}
        absolute_download_dir_path = absolute_download_path / f'{model_lowercase}_{model_id}'
        relative_download_dir_path = relative_download_path / f'{model_lowercase}_{model_id}'
        file_objs = list()
        for download_data in download_datas:
            file_name = sanitize_filename(download_data.file_name)
            if len(file_name) > 75:
                file_name = file_name[:30] + '_' + file_name[-35::1]
            if file_name in existing_file_names:
                continue
            absolute_path = absolute_download_dir_path / file_name
            relative_path = relative_download_dir_path / file_name
            if absolute_path.suffix not in allowable_formats:
                continue
            if download_data.method == 'GET' and not download_files_from_get_url:
                paths = [None]
            else:
                Path(absolute_download_dir_path).mkdir(parents=True, exist_ok=True)
                paths = DownloadFiles.request_to_download_general(
                    download_data=download_data, absolute_path=absolute_path, relative_path=relative_path
                )
            for path in paths:  # type: pathlib.Path
                file_objs.append(File(
                    name=path.name if path else file_name, path=path.as_posix() if path else None,
                    url=str(download_data.url) if download_data.method == 'GET' else None,
                    model_type=model_type, model_id=model_id
                ))
        session.add_all(file_objs)


if __name__ == '__main__':
    DBHelper.add_regions()
    DBHelper.add_cities()
    DBHelper.add_addresses()
    DBHelper.add_trading_floors()
