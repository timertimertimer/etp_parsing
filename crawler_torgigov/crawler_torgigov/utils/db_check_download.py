import asyncio
import json

import aiomysql

from crawler_torgigov.python_mysql_dbconfig import read_db_config
from crawler_torgigov.utils.config import tables

TABLE = tables['table_torgi_gov_bankrot']

connection_dict = read_db_config()


async def async_check_download(loop, trading_id):
    pool = await aiomysql.create_pool(host=connection_dict['host'],
                                      port=int(connection_dict['port']),
                                      db=connection_dict['database'],
                                      user=connection_dict['user'],
                                      password=connection_dict['password'],
                                      loop=loop)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f" SELECT files FROM {TABLE} where trading_id='{trading_id}' ")
            try:
                (r,) = await cur.fetchone()
                if r:
                    return json.loads(r)
                else:
                    return None
            except:
                return None

    pool.close()
    await pool.wait_closed()


loop = asyncio.get_event_loop()

# async def connect_db():
#     db = Database(f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
#     await db.connect()
#     return db
#
# async def disconnect_db(db):
#     await db.disconnect()
#
# async def fetch(trading_id):
#     db = await connect_db()
#     query = f"select files from lots_torgigov_bankrot where trading_id={trading_id}"
#     rows = await db.fetch_all(query)
#     await disconnect_db(db)
#     return rows
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(fetch('49532817'))
