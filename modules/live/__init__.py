import asyncio, importlib, functools
from utils import common, exceptions
from pathlib import Path
from bilibili_api import live

cfgPath = str(Path(common.getRunningPath()).resolve()/'config'/'live.json')
logger = common.getLogger('live')
config = common.loadConfig(logger = logger, cfgPath = cfgPath)
rooms = {}
receivers = {}

async def main():
    global receivers
    global rooms
    tasks = []
    if not config:
        logger.warning('未配置直播间')
        return
    if config.get('disable', False):
        logger.debug('live插件已禁用')
        return
    load_plugins()
    for room in config['rooms']:
        rid = room['room']
        if room.get('disable', False):
            logger.debug(f"直播间{rid}被禁用，已跳过")
            continue
        logger.info(f'开启直播间{rid}')
        plugins = room.get('plugins', [])
        if not plugins:
            logger.warning(f'直播间{rid}未配置插件，已跳过')
            continue
        rooms[rid] = live.LiveDanmaku(rid)
        for plugin in plugins:
            if plugin in receivers:
                logger.debug(f'加载插件{plugin}')
                for receiver in receivers[plugin]:
                    for rtype in receiver['type']:
                        rooms[rid].add_event_handler(rtype, receiver['func'])
            else:
                logger.warning(f'{plugin}插件不存在，请检查')
        tasks.append(rooms[rid].connect(return_task = True))
    await asyncio.gather(checkConnect(), *tasks)

def load_plugins():
    logger.info('导入直播插件中....')
    plugin_dir = Path(__file__).parent
    module_prefix = plugin_dir.resolve().name

    for plugin in plugin_dir.iterdir():
        if plugin.is_dir() \
                and not plugin.name.startswith('_') \
                and plugin.joinpath('__init__.py').exists():
            importlib.import_module(f'modules.live.{plugin.name}')
        elif not plugin.name.startswith('_') and plugin.suffix == '.py':
            importlib.import_module(f'modules.live.{plugin.name[:-3]}')
    
    if not receivers:
        logger.warning('live目录下不存在可用插件')
    else:
        logger.info('插件导入完成')

async def checkConnect():
    global rooms
    try_times = {}
    check_interval = config.get('check_interval', 10)
    reconnect_times = config.get('reconnect_times', 3)
    while True:
        await asyncio.sleep(check_interval)
        for k,v in rooms.items():
            if not v.has_connected():
                if try_times[k] >= reconnect_times:
                    logger.warning(f'直播间{v.room_display_id}断连次数过多，停止重连')
                    rooms.pop(k)
                    continue
                try_times[k] = try_times.get(k, 0) + 1
                logger.warning(f'直播间{v.room_display_id}已断开连接，正在进行第{try_times.get(k)}次重连')
                v.connect(return_task = True)
            else:
                try_times[k] = 0
                

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