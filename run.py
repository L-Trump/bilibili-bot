import json, os, time, asyncio, logging
from bilibili_api import live, user, Verify
from utils import bililogin, common
import modules

logger = common.getLogger('bot')
config = common.loadConfig(logger = logger)

def main():
    verify = common.getVerify()
    print(f"SESSDATA: {verify.sessdata} CSRF:{verify.csrf}")
    loop = asyncio.get_event_loop()
    try:
        task = loop.create_task(modules.load_modules())
        loop.run_until_complete(task)
    except:
        raise

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('用户按键退出，程序停止')