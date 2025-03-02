import csv
import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import PurePath

from sqlalchemy import create_engine, text, select, and_, or_
from sqlalchemy.orm import sessionmaker, joinedload, aliased
from typing import Type

from general_utils.config import data_path
from general_utils.models import (
    Auction, ParserStatus, TradingFloor, Address, Region, City, Counterparty, Lot, LotPeriod, File, LegalCase, Base
)
from general_utils.models.counterparty import CounterpartySRO, DebtorCategory, CounterpartyDebtorCategory
from general_utils.models.file import FileModelType
from general_utils.models.parser_status import StatusType
from general_utils.python_mysql_dbconfig import read_db_config

logger = logging.getLogger(__name__)
db_config = read_db_config()
connection_string = f'mysql+pymysql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}'

engine = create_engine(connection_string, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    DBHelper.set_wait_timeout(db)
    return db


@contextmanager
def db_context():
    db = SessionLocal()
    DBHelper.set_wait_timeout(db)
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Error in db_context: {e}")
        raise
    finally:
        db.close()


class DBHelper:
    @staticmethod
    def set_wait_timeout(session, timeout=600):
        """Устанавливает wait_timeout для текущей сессии."""
        try:
            session.execute(text(f"SET SESSION wait_timeout = {timeout};"))
            session.commit()
            logger.info(f"Session wait_timeout set to {timeout} seconds.")
        except Exception as err:
            logger.warning(f"Error setting wait_timeout: {err}")
            session.rollback()

    @staticmethod
    def get_latest_lot(crawler_name: str, data_origin_url: str, keys=None, day: int = 30) -> tuple[list, int] | None:
        date_threshold = datetime.utcnow() - timedelta(days=day)
        if keys is None:
            keys = [Auction.url]
        if not isinstance(keys, list):
            keys = [keys]
        with db_context() as session:
            try:
                trading_floor_id = session.scalars(
                    select(ParserStatus.trading_floor_id).where(ParserStatus.name == crawler_name)
                ).first()
                if trading_floor_id is None:
                    logger.info(
                        f"get_latest_lot :: trading_floor_id not found for crawler {crawler_name}. Creating new record."
                    )
                    trading_floor_id = session.scalars(
                        select(TradingFloor.id).where(TradingFloor.url == data_origin_url)
                    ).first()
                    if trading_floor_id is None:
                        logger.error(f"get_latest_lot :: TradingFloor not found for URL {data_origin_url}. Skipping.")
                        return (None, None)
                    new_parser_status = ParserStatus(name=crawler_name, trading_floor_id=trading_floor_id)
                    session.add(new_parser_status)
                    session.commit()
                    return [], trading_floor_id
                stmt = select(*keys).where(
                    and_(Auction.created_at >= date_threshold, Auction.trading_floor_id == trading_floor_id)
                )
                lots = session.scalars(stmt).all()
                return lots, trading_floor_id

            except Exception as e:
                logger.error(f"get_latest_lot :: {e}")
                session.rollback()  # Откатываем транзакцию в случае ошибки
                return []

    @staticmethod
    def update_status(status: bool, spider_name: str):
        with db_context() as session:
            try:
                new_status = StatusType.active if status else StatusType.disabled
                parser = session.query(ParserStatus).filter(ParserStatus.name == spider_name).first()
                if parser:
                    parser.status = new_status
                    parser.updated_at = datetime.utcnow()
                    session.commit()
                else:
                    logger.warning(f"update_status :: ParserStatus with name '{spider_name}' not found.")
            except Exception as e:
                logger.error(f"update_status :: {e}")
                session.rollback()

    @staticmethod
    def save_counter_and_duration(counter: int, duration: float, spider_name: str):
        with db_context() as session:
            try:
                parser = session.query(ParserStatus).filter(ParserStatus.name == spider_name).first()
                if parser:
                    parser.counter = counter
                    parser.duration = duration
                    parser.updated_at = datetime.utcnow()
                    session.commit()
                else:
                    logger.warning(f"save_counter_and_duration :: ParserStatus with name '{spider_name}' not found.")
            except Exception as e:
                logger.error(f"save_counter_and_duration :: {e}")
                session.rollback()

    @staticmethod
    def get_addresses():
        with db_context() as session:
            return session.query(Address).all()

    @staticmethod
    def get_addresses_with_regions():
        with db_context() as session:
            return session.query(Address).options(joinedload(Address.region)).all()

    @staticmethod
    def get_region_names():
        with db_context() as session:
            return session.scalars(select(Region.name)).all()

    @staticmethod
    def get_cities_with_regions():
        with db_context() as session:
            return session.query(City).options(joinedload(City.region)).all()

    @staticmethod
    def get_all(model: Type[Base]):
        with db_context() as session:
            query = session.query(model)
            if model is TradingFloor:
                query = query.options(joinedload(TradingFloor.counterparty).joinedload(Counterparty.sro_memberships))
            elif model is LegalCase:
                query = query.options(joinedload(LegalCase.auction).joinedload(Auction.debtor))
            elif model is Counterparty:
                query = query.options(joinedload(Counterparty.sro_memberships))
            elif model is Auction:
                query = query.options(joinedload(Auction.legal_case))
            return query.all()

    @staticmethod
    def get_regions_dict():
        with db_context() as session:
            return {region.name: region.id for region in session.query(Region).all()}

    @staticmethod
    def add_regions():
        regions = []
        with open(data_path / 'regions_with_oktmo.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=':')
            for row in reader:
                regions.append(Region(oktmo=row['oktmo'], name=row['region']))

        with db_context() as session:
            session.add_all(regions)
            session.commit()

    @staticmethod
    def add_addresses(source_path: PurePath = data_path / 'addresses.csv', addresses: list[City] = None):
        addresses = addresses or []
        regions = DBHelper.get_regions_dict()
        if not addresses:
            with open(source_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if id_ := regions.get(row['region']):
                        addresses.append(Address(region_id=id_, name=row['address']))
                    else:
                        pass
        with db_context() as session:
            session.add_all(addresses)
            session.commit()

    @staticmethod
    def add_cities(source_path: PurePath = data_path / 'cities.csv', cities: list[City] = None):
        cities = cities or []
        regions = DBHelper.get_regions_dict()
        if not cities:
            with open(source_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if id_ := regions.get(row['region']):
                        cities.append(City(region_id=id_, name=row['city']))
                    else:
                        pass
        with db_context() as session:
            session.add_all(cities)
            session.commit()

    @staticmethod
    def add_trading_floors(
            source_path: PurePath = data_path / 'trading_floors.csv', trading_floors: list[TradingFloor] = None
    ):
        trading_floors = trading_floors or []
        if not trading_floors:
            with open(source_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    trading_floors.append(TradingFloor(name=row['name'], url=row['url']))
        with db_context() as session:
            session.add_all(trading_floors)
            session.commit()

    @staticmethod
    def store_item(item, trading_floor_id, session=None):
        session = session or SessionLocal()
        try:
            organizer_id, arbitrator_id, debtor_id = DBHelper.store_and_get_counterparty_ids(item, session)
            auction_id = DBHelper.store_and_get_auction_id(
                item, organizer_id, arbitrator_id, debtor_id, trading_floor_id, session
            )
            if item['case_number']:
                DBHelper.store_legal_case_id(item, auction_id, session)
            else:
                pass
            lot_id = DBHelper.store_and_get_lot_id(item, auction_id, session)
            DBHelper.store_lot_period(item, lot_id, session)
            DBHelper.store_files(item, lot_id, auction_id, session)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"store_item error: {e}")
            raise e

    @staticmethod
    def get_or_create_address(address_str, session):
        if not address_str:
            return
        from general_utils.location import RegionIdentifier
        address = session.query(Address).filter_by(name=address_str).first()
        if not address:
            address = Address(name=address_str)
            region_name = RegionIdentifier.get_region(address_str)
            if region_name:
                if region := session.query(Region).filter_by(name=region_name).first():
                    address.region_id = region.id
                else:
                    logger.warning(f"Region oktmo with name {region_name} not found.")
            session.add(address)
            session.commit()
        return address

    @staticmethod
    def get_or_create_debtor_category(category_name, session):
        category = session.query(DebtorCategory).filter_by(name=category_name).first()
        if not category:
            category = DebtorCategory(name=category_name)
            session.add(category)
            session.commit()
        return category

    @staticmethod
    def get_counterparty(session: SessionLocal, inn: str = None, name: str = None, short_name: str = None):
        query = session.query(Counterparty)
        if inn and name:
            query = query.filter(or_(Counterparty.inn == inn, Counterparty.name == name))
        elif inn:
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
    def get_legal_case(number: str, session: SessionLocal):
        return session.query(LegalCase).filter(LegalCase.number == number).first()

    @staticmethod
    def get_counterparty_debtor_category(counterparty_id: int, debtor_category_id: int, session: SessionLocal):
        return (
            session.query(CounterpartyDebtorCategory)
            .filter(counterparty_id == counterparty_id, debtor_category_id == debtor_category_id).first()
        )

    @staticmethod
    def store_model(model: Base, session):
        logger.info(f'Storing model {model}')
        try:
            if isinstance(model, Counterparty):
                if session.query(Counterparty).filter_by(inn=model.inn).first():
                    session.merge(model)
                    session.commit()
                    return model
            session.add(model)
            session.commit()
            return model
        except Exception as e:
            session.rollback()
            raise e

    @staticmethod
    def store_and_get_counterparty_ids(item, session):
        organizer_counterparty = DBHelper.get_counterparty(
            inn=item['trading_org_inn'], name=item['trading_org'], session=session
        )
        if not organizer_counterparty:
            trading_org_contacts = json.loads(item['trading_org_contacts'])
            organizer_counterparty = Counterparty(
                inn=item['trading_org_inn'],
                name=item['trading_org'],
                email=trading_org_contacts.get('email'),
                phone=trading_org_contacts.get('phone'),
            )
            session.add(organizer_counterparty)
            session.commit()

        arbitrator_counterparty = DBHelper.get_counterparty(
            inn=item['arbit_manager_inn'], name=item['arbit_manager'], session=session
        )
        if not arbitrator_counterparty:
            arbitrator_counterparty = Counterparty(inn=item['arbit_manager_inn'], name=item['arbit_manager'])
            session.add(arbitrator_counterparty)
            session.commit()

        debtor_counterparty = DBHelper.get_counterparty(inn=item['debtor_inn'], session=session)
        if not debtor_counterparty:
            debtor_counterparty = Counterparty(inn=item['debtor_inn'])
            if item['address']:
                address = DBHelper.get_or_create_address(item['address'], session)
                debtor_counterparty.address_id = address.id
            session.add(debtor_counterparty)
            session.commit()
        return organizer_counterparty.id, arbitrator_counterparty.id, debtor_counterparty.id

    @staticmethod
    def store_and_get_auction_id(item, organizer_id, arbitrator_id, debtor_id, trading_floor_id, session):
        trade = session.query(Auction).filter_by(ext_id=item['trading_id']).first()
        if not trade:
            trade = Auction(
                ext_id=item['trading_id'],
                url=item['trading_link'],
                number=item.get('trading_number'),
                type=item.get('trading_type'),
                form=item.get('trading_form'),
                message_number=item.get('msg_number'),
                organizer_id=organizer_id,
                arbitrator_id=arbitrator_id,
                debtor_id=debtor_id,
                trading_floor_id=trading_floor_id,
            )
            session.add(trade)
            session.commit()
        return trade.id

    @staticmethod
    def store_legal_case_id(item, auction_id, session):
        legal_case = session.query(LegalCase).filter_by(number=item['case_number']).first()
        if not legal_case:
            legal_case = LegalCase(
                number=item['case_number'],
                auction_id=auction_id,
            )
            session.add(legal_case)
            session.commit()

    @staticmethod
    def store_and_get_lot_id(item, auction_id, session):
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
                auction_id=auction_id,
            )
            session.add(lot)
            session.commit()
        return lot.id

    @staticmethod
    def store_lot_period(item, lot_id, session):
        lot_period = session.query(LotPeriod).filter_by(lot_id=lot_id).first()
        if not lot_period:
            if item['step_price']:
                lot_period = LotPeriod(
                    request_start_at=item['start_date_requests'],
                    request_end_at=item['end_date_requests'],
                    trading_start_at=item['start_date_trading'],
                    trading_end_at=item['end_date_trading'],
                    price=item['step_price'],
                    lot_id=lot_id,
                )
                session.add(lot_period)
            elif periods := item['periods']:
                for period in json.loads(periods):
                    lot_period = LotPeriod(
                        request_start_at=period['start_date_requests'],
                        request_end_at=period['end_date_requests'],
                        trading_start_at=period['start_date_requests'],
                        trading_end_at=period['end_date_trading'],
                        price=period['current_price'],
                        lot_id=lot_id,
                    )
                    session.add(lot_period)

    @staticmethod
    def store_files(item, lot_id, auction_id, session):
        files = json.loads(item['files'])
        general_files = files['general']
        storage_files = session.query(File).filter_by(model_type=FileModelType.Auction, model_id=auction_id).all()
        storage_file_names = {file.name for file in storage_files}
        for file in general_files:
            if file['original_name'] not in storage_file_names:
                file_obj = File(
                    name=file['original_name'],
                    path=file['link'],
                    url=file['link_etp'],
                    model_type=FileModelType.Auction,
                    model_id=auction_id
                )
                session.add(file_obj)

        lot_files = files['lot']
        storage_files = session.query(File).filter_by(model_type=FileModelType.Lot, model_id=lot_id).all()
        storage_file_names = {file.name for file in storage_files}
        for file in lot_files:
            if file['original_name'] not in storage_file_names:
                file_obj = File(
                    name=file['original_name'],
                    path=file['link'],
                    url=file['link_etp'],
                    model_type=FileModelType.Lot,
                    model_id=lot_id
                )
                session.add(file_obj)


if __name__ == '__main__':
    DBHelper.add_regions()
