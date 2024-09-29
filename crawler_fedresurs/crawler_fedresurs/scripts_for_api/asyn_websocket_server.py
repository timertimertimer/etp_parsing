# -*- coding: utf-8 -*-
import asyncio
import json
import os
import pickle
import socket
import subprocess
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path

import websockets

SERVER = 'localhost'
PORT = 55555

ROOT_DIR = '/home/parser'
RELATIVE_PATH_ARBITR = '/etp_parsing/crawler_fedresurs/crawler_fedresurs/json_task_data/task_arbitr/'
RELATIVE_PATH_DEBITOR = '/etp_parsing/crawler_fedresurs/crawler_fedresurs/json_task_data/task_debitr/'
RELATIVE_PATH_ORGANIZER = '/etp_parsing/crawler_fedresurs/crawler_fedresurs/json_task_data/task_organizer/'

ARBITR_NAME = 'arbitrator'
ORG_NAME = 'organizer'
#ORG_COMPANY = 'organizer_company'
DEBITOR = 'debtor'


def create_dir(root_dir, dir_name):
    return Path(f'{root_dir}{dir_name}').mkdir(parents=True, exist_ok=True)

def return_parse_date():
    return datetime.now().strftime('%Y_%m_%d_%H_%M_%S')


async def write_arbitr_json(data):
    create_dir(ROOT_DIR, RELATIVE_PATH_ARBITR)
    with open(f'{ROOT_DIR}{RELATIVE_PATH_ARBITR}post_data_arbitr_{return_parse_date()}.json', 'w',
              encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


async def write_organizer_json(data):
    create_dir(ROOT_DIR, RELATIVE_PATH_ORGANIZER)
    with open(f'{ROOT_DIR}{RELATIVE_PATH_ORGANIZER}post_data_organizer_{return_parse_date()}.json', 'w',
              encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


async def write_debitor_json(data):
    create_dir(ROOT_DIR, RELATIVE_PATH_DEBITOR)
    with open(f'{ROOT_DIR}{RELATIVE_PATH_DEBITOR}post_data_debitor_{return_parse_date()}.json', 'w',
              encoding='utf-8') as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))


async def sort_task_data(dict_: dict):
    """write data for parsing to specific json file according params and return tuple with 0(not) or 1(execute) what spiders execute"""
    Manager = namedtuple('Manager', 'arbitr, organizer, debitor')
    arbitr_ = 0
    organizer_ = 0
    debitor_ = 0
    for k, v in dict_.items():
        if k == ORG_NAME:
            data = dict()
            if len(v) > 0:
                data[k] = v
                await write_organizer_json(data)
                organizer_ = 1
                time.sleep(1)
                del data
        # elif k == ORG_COMPANY:
        #     data = dict()
        #     if len(v) > 0:
        #         data[k] = v
        #         await write_organizer_json(data)
        #         organizer_ = 1
        #         time.sleep(1)
        #         del data
        elif k == ARBITR_NAME:
            data = dict()
            if len(v) > 0:
                data[k] = v
                await write_arbitr_json(data)
                arbitr_ = 1
                time.sleep(0.5)
                del data
        elif k == DEBITOR:
            data = dict()
            if len(v) > 0:
                data[k] = v
                await write_debitor_json(data)
                debitor_ = 1
                del data
        else:
            continue
    manager = Manager(arbitr=arbitr_, organizer=organizer_, debitor=debitor_)
    return manager


PATH_SPIDERS_START = f'{ROOT_DIR}/etp_parsing/crawler_fedresurs/crawler_fedresurs/shell_scripts/'


async def run_arbitr():
    """if manger.arbitr == 1 -> run spider fedres_arbitor"""
    current_dir = os.getcwd()
    os.chdir(PATH_SPIDERS_START)
    subprocess.run(['./start_fedres_arbitr.sh'])
    os.chdir(current_dir)


async def run_organizer():
    """if manger.organizer == 1 -> run spider fedres_organizer"""
    current_dir = os.getcwd()
    os.chdir(PATH_SPIDERS_START)
    subprocess.run(['./start_fedres_organizer.sh'])
    os.chdir(current_dir)


async def run_debitr():
    """if manger.debitor == 1 -> run spider fedres_debitor"""
    current_dir = os.getcwd()
    os.chdir(PATH_SPIDERS_START)
    subprocess.run(['./start_fedres_debitor.sh'])
    os.chdir(current_dir)


# run server and execute spiders
async def response(websocket, path):
    message = await websocket.recv()
    data_dict = pickle.loads(message)
    #print(f'We got the messsage from the client: {data_dict}')
    manager = await sort_task_data(data_dict)

    if manager.arbitr == 1:
        await run_arbitr()
        await asyncio.sleep(2)
    if manager.organizer == 1:
        await run_organizer()
        await asyncio.sleep(2)
    if manager.debitor == 1:
        await run_debitr()
        await asyncio.sleep(2)
    # await websocket.send('I can confirm I got your messag!')


start_server = websockets.serve(response, SERVER, PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
