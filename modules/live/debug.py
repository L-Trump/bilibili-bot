import modules, time
from pathlib import Path
from utils import common, exceptions
from bilibili_api import live, user, Verify
from utils.cache import cachedRun as cache

logger = common.getLogger('live_debug')
@modules.live.receiver('debug', 'ALL')
async def on_all(msg):
    Filter = [
        'ROOM_REAL_TIME_MESSAGE_UPDATE', 
        'DANMU_MSG', 
        'COMBO_SEND',
        'ROOM_BANNER', 
        'SEND_GIFT',
        'WELCOME', 
        'INTERACT_WORD', 
        'VIEW', 
        'ENTRY_EFFECT', 
        'NOTICE_MSG', 
        'PANEL', 
        'USER_TOAST_MSG', 
        'ONLINERANK', 
        'ROOM_RANK', 
        'WELCOME_GUARD', 
        'ACTIVITY_BANNER_UPDATE_V2'
    ]
    path = Path(common.getRunningPath()) / 'debug' / 'live' / msg['type']
    if path.exists():
        if msg['type'] in Filter: return
        if msg['type'] == 'SEND_GIFT' and msg['data']['data']['coin_type'] == 'silver': return
        if msg['type'] == 'SEND_GIFT' and msg['data']['data']['total_coin'] < 10000: return
    upinfo = cache(user.get_user_info, cache(live.get_room_play_info, msg['room_display_id'], verify=None).get('uid'))
    upname = upinfo.get('name')
    rq = time.strftime('%H-%M-%S', time.localtime(time.time()))
    savePath = Path(common.getRunningPath()) / 'debug' / 'live' / msg['type'] / f'{upname}-{msg["type"]}-{rq}-{int(time.mktime(time.localtime(time.time())))}.json'
    savePath = str(savePath)
    logger.info(f'保存了一条{upname}的{msg["type"]}消息')
    common.saveConfig(msg, savePath, logger=logger)