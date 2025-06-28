import time

from pymysql.err import OperationalError, ProgrammingError
from sqlalchemy.exc import SQLAlchemyError

from app.db.db_helper import DBHelper
from app.utils import logger


class BasePipeline:
    async def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, None)

        attempt = 0
        while attempt < 5:
            try:
                DBHelper.store_item(item, spider.trading_floor_id)
                spider.counter += 1
                logger.info(f"Stored {spider.counter} lots")
                return item
            except (ProgrammingError, OperationalError) as e:
                error_msg = str(e)
                if any(
                    [
                        "MySQL Connection not available" in error_msg
                        or "Lost connection to MySQL server" in error_msg
                    ]
                ):
                    logger.warning(
                        f"MySQL connection lost. Retrying... (Attempt {attempt + 1}/5)"
                    )
                    DBHelper.session.close()
                    DBHelper.create_new_connection()
                    attempt += 1
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Database error: {e}")
                    DBHelper.session.rollback()
                    break
            except SQLAlchemyError as e:
                error_msg = str(e.orig)
                if any(
                    [
                        "MySQL Connection not available" in error_msg
                        or "Lost connection to MySQL server" in error_msg
                    ]
                ):
                    logger.warning(
                        f"MySQL connection lost. Retrying... (Attempt {attempt + 1}/5)"
                    )
                    DBHelper.session.close()
                    DBHelper.create_new_connection()
                    attempt += 1
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Database error: {e}")
                    DBHelper.session.rollback()
                    break
            except Exception as e:
                logger.error(f"Error: {e}")
                DBHelper.session.rollback()
                break
        return item
