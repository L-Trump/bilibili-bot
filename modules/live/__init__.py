import asyncio, importlib, functools
from utils import common, exceptions
from pathlib import Path
from bilibili_api import live, user, Verify

cfgPath = str(Path(__file__).resolve().parent / 'config.json')
logger = common.getLogger('live')
config = common.loadConfig(logger = logger, cfgPath = cfgPath)
rooms = {}
receivers = {}
verify = None
# if config['needVerify']:
    # pass

async def main():
    global receivers
    tasks = []
    if not config:
        logger.warning('未配置直播间')
        return
    load_plugins()
    for k,v in config.items():
        if 'disable' in v and v['disable']: continue
        logger.info(f'开启直播间{k}')
        plugins = v['plugins'] if 'plugins' in v else []
        if not plugins:
            logger.warning(f'直播间{k}未配置插件，已跳过')
            continue
        rooms[str(k)] = live.LiveDanmaku(int(k), verify = verify)
        for plugin in plugins:
            if plugin in receivers:
                logger.debug(f'加载插件{plugin}')
                for receiver in receivers[plugin]:
                    for rtype in receiver['type']:
                        rooms[str(k)].add_callback(rtype, receiver['func'])
            else:
                logger.warning(f'{plugin}插件不存在，请检查')
        tasks.append(rooms[str(k)].connect(return_task = True))
    await asyncio.gather(*tasks)

def load_plugins():
    logger.info('导入直播插件中....')
    plugin_dir = Path(__file__).parent
    module_prefix = plugin_dir.resolve().name

    for plugin in plugin_dir.iterdir():
        if plugin.is_dir() \
                and not plugin.name.startswith('_') \
                and plugin.joinpath('__init__.py').exists():
            importlib.import_module(f'{module_prefix}.{plugin.name}')
        elif not plugin.name.startswith('_') and plugin.suffix == '.py':
            print(plugin.name)
            importlib.import_module(f'modules.live.{plugin.name[:-3]}')
    
    if not receivers:
        logger.warning('live目录下不存在可用插件')
    else:
        logger.info('插件导入完成')

def receiver(name: str, *receiverType):
    global receivers
    def decoration(func):
        if name not in receivers:
            receivers[name] = []
        receiver = {
            'func': func,
            'type': []
        }
        for rtype in receiverType:
            receiver['type'].append(rtype.upper())
        receivers[name].append(receiver)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        return wrapper
    return decoration