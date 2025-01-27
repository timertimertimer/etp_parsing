from pprint import pprint

from crawler_torgigov.utils.db import *
from crawler_torgigov.utils.db_check_download import *

a = loop.run_until_complete(
    async_check_download(loop, trading_id='49532817'))
if a and isinstance(dict, a):
    pprint(a)
