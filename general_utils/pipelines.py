import logging
import time

import sqlalchemy.exc
from pymysql.err import OperationalError, ProgrammingError
from sqlalchemy.exc import SQLAlchemyError

from .db import get_db, DBHelper

logger = logging.getLogger(__name__)


class BasePipeline:
    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        self.session = get_db()

    def close_spider(self, spider):
        if self.session:
            self.session.commit()
            self.session.close()

    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, None)

        attempt = 0
        while attempt < 5:
            try:
                DBHelper.store_item(item, spider.trading_floor_id, session=self.session)
                spider.counter += 1
                logger.info(f'Stored {spider.counter} lots')
                return item
            except (ProgrammingError, OperationalError) as e:
                error_msg = str(e)
                if any([
                    "MySQL Connection not available" in error_msg or
                    "Lost connection to MySQL server" in error_msg
                ]):
                    logger.warning(f"MySQL connection lost. Retrying... (Attempt {attempt + 1}/5)")
                    self.session.close()
                    self.session = get_db()
                    attempt += 1
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Database error: {e}")
                    self.session.rollback()
                    break
            except SQLAlchemyError as e:
                error_msg = str(e.orig)
                if any([
                    "MySQL Connection not available" in error_msg or
                    "Lost connection to MySQL server" in error_msg
                ]):
                    logger.warning(f"MySQL connection lost. Retrying... (Attempt {attempt + 1}/5)")
                    self.session.close()
                    self.session = get_db()
                    attempt += 1
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Database error: {e}")
                    self.session.rollback()
                    break
            except Exception as e:
                logger.error(f"Error: {e}")
                self.session.rollback()
                break
        return item
