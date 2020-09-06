import modules
from pathlib import Path
from utils import common, exceptions
from utils.cache import cachedRun as cache
from bilibili_api import live, user, Verify, Danmaku

logger = common.getLogger('live')
cfgDir = str(Path(common.getRunningPath()) / 'config' / 'live_gift.json')
config = common.loadConfig(cfgDir, logger = logger)
verify = common.getVerify()

@modules.live.receiver('gift', 'SEND_GIFT')
async def on_gift(msg):
    if not Filter_Gift(msg): return
    data = msg['data']['data']
    notice_str = getConf(msg['room_display_id'], 'gift', 'str')
    MSG = notice_str.format(**data)
    sendMsg(msg['room_real_id'], MSG)

@modules.live.receiver('gift', 'GUARD_BUY')
async def on_guard(msg):
    if not Filter_Guard(msg): return
    data = msg['data']['data']
    notice_str = getConf(msg['room_display_id'], 'guard', 'str')
    MSG = notice_str.format(**data)
    sendMsg(msg['room_real_id'], MSG)

@modules.live.receiver('gift', 'SUPER_CHAT_MESSAGE')
async def on_sc(msg):
    if not Filter_Guard(msg): return
    data = msg['data']['data']
    notice_str = getConf(msg['room_display_id'], 'sc', 'str')
    MSG = notice_str.format(**data)
    sendMsg(msg['room_real_id'], MSG)

DEFAULT_CONFIG = {
    "gift": {
        "disable": False,
        "silver": False,
        "min_silver_coin": 100,
        "gold": True,
        "min_gold_coin": 5000,
        "str": "感谢{uname}{action}的{num}个{giftName}"
    },
    "guard": {
        "disable": False,
        "str": "感谢{username}老板的{gift_name}"
    },
    "sc": {
        "disable": False,
        "min_price": 30,
        "str": "感谢{user_info{uname}}老板的SC"
    }
}

def formatConf():
    global config
    if 'global' not in config:
        config['global'] = {}
    for k,v in DEFAULT_CONFIG.items():
        if k not in config['global']:
            config['global'][k] = v
    common.saveConfig(config, cfgDir, logger = logger)

def getConf(rid, module, cfg):
    rid = str(rid)
    if module in config.get(rid, {}) and cfg in config[rid][module]:
        return config[rid][module][cfg]
    if module in config.get('global', {}) and cfg in config['global'][module]:
        return config['global'][module][cfg]
    return DEFAULT_CONFIG.get(module, {}).get(cfg, None)

def Filter_Gift(msg):
    data = msg['data']['data']
    rid = msg['room_display_id']
    if getConf(rid, 'gift', 'disable'): return False
    if not getConf(rid, 'gift', 'silver') and data['coin_type'] == 'silver': return False
    if data['coin_type'] == 'silver' and data['total_coin'] < getConf(rid, 'gift', 'min_silver_coin'): return False
    if not getConf(rid, 'gift', 'gold') and data['coin_type'] == 'gold': return False
    if data['coin_type'] == 'gold' and data['total_coin'] < getConf(rid, 'gift', 'min_gold_coin'): return False
    return True

def Filter_Guard(msg):
    data = msg['data']['data']
    rid = msg['room_display_id']
    if getConf(rid, 'guard', 'disable'): return False
    return True

def Filter_SC(msg):
    data = msg['data']['data']
    rid = msg['room_display_id']
    if getConf(rid, 'sc', 'disable'): return False
    if data['price'] < getConf(rid, 'sc', 'min_price'): return False
    return True

def sendMsg(rid, msg):
    upinfo = cache(user.get_user_info, cache(live.get_room_play_info, rid, verify=None).get('uid'))
    upname = upinfo.get('name')
    danmu = Danmaku(text = str(msg), mode = 1)
    live.send_danmaku(rid, danmaku = danmu, verify = verify)
    logger.info(f'{upname}的直播间--' + msg + '--已发送')