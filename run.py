import asyncio
from utils import common
import modules

logger = common.getLogger('bot')
config = common.loadConfig(logger = logger)

def main():
    logger.info('机器人启动')
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