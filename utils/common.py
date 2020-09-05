import logging
import time
import json
import importlib
from pathlib import Path
from bilibili_api import Verify

def newLogger(loggerName: str, debug: bool = False, file: bool = True):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.INFO if not debug else logging.DEBUG)
    formatter = logging.Formatter("[" + loggerName + "][%(asctime)s][%(levelname)s] %(message)s")
    ConsoleHandler = logging.StreamHandler()
    ConsoleHandler.setFormatter(formatter)
    logger.addHandler(ConsoleHandler)
    if file:
        rq = time.strftime('%Y%m%d-%H-%M-%S', time.localtime(time.time()))
        log_path = getRunningPath(False).joinpath('logs', loggerName)
        checkPath(log_path)
        logfile = log_path / f"{rq}.log"
        mode = 'a+' if logfile.exists else 'w+'
        FileHandler = logging.FileHandler(str(logfile), mode=mode, encoding="utf-8")
        FileHandler.setFormatter(formatter)
        logger.addHandler(FileHandler)
    return logger

def getLogger(loggerName: str, debug: bool = False, file: bool = True):
    logger = logging.getLogger(loggerName)
    if logger.hasHandlers():
        return logger
    return newLogger(loggerName, debug = debug, file = file)

def getRunningPath(return_string: bool = True):
    if return_string:
        return str(Path(__file__).resolve().parent.parent)
    else:
        return Path(__file__).resolve().parent.parent

def getApi():
    with open(getRunningPath() + "/utils/data/api.json", "r", encoding="utf-8") as f:
        apis = json.loads(f.read())
        f.close()
    return apis

def checkPath(path = None, Dir: str = None, create: bool = True):
    path = path.resolve()
    if path.exists(): return True
    if create:
        path.mkdir(parents=True)
        return True
    else:
        return False

def loadConfig(cfgPath: str = str(getRunningPath(False) / 'config' / 'bot.json'), logger = getLogger('bot')):
    config = {}
    logger.debug('加载配置文件...')
    path = Path(cfgPath)
    checkPath(path.parent)
    if path.exists:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.debug('配置加载成功')
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{}')
        logger.debug('配置文件不存在，已自动创建')
    return config
        
def saveConfig(config={}, cfgPath: str = str(getRunningPath(False) / 'config' / 'bot.json'), logger = getLogger('bot')):
    logger.debug('保存配置文件...')
    path = Path(cfgPath)
    checkPath(path.parent)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent = 4, ensure_ascii = False)
    logger.debug('保存成功')

def getVerify(logger = getLogger('bot')):
    config = loadConfig(logger=logger)
    if 'account' in config and 'sessdata' in config['account']:
        logger.debug('发现本地账号，验证是否有效...')
        verify = Verify(sessdata = config['account']['sessdata'], csrf = config['account']['bili_jct'])
        ck = verify.check()
        if ck.get('code') != 0:
            logger.warning('本地记录的账号失效，重新登录...')
            logger.debug(f'错误代码:{ck["code"]}, 错误原因:{ck["message"]}')
        else:
            logger.debug('获取Verify成功')
            return verify

    return loginBilibili()

def loginBilibili(logger = getLogger('bot')):
    config = loadConfig(logger=logger)
    logger.info('账号登录中...')
    importlib.import_module('utils.bililogin')
    verify = bililogin.login_QR()
    config['account'] = {}
    config['account']['sessdata'] = verify.sessdata
    config['account']['bili_jct'] = verify.csrf
    saveConfig(config = config, logger = logger)
    return verify