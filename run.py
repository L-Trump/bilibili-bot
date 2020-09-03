import json, os, time, asyncio, logging
from bilibili_api import live, user, Verify
from utils import bililogin, common
import modules

logger = common.getLogger('bot')
config = common.loadConfig(logger = logger)

def main():
    verify = common.getVerify()
    print(f"SESSDATA: {verify.sessdata} CSRF:{verify.csrf}")
    try:
        asyncio.run(modules.load_modules())
    except:
        raise

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning('用户按键退出，程序停止')