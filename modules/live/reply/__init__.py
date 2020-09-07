import modules, re, time
import asyncio
from .container import Queue, TTLCheck
from utils import common, exceptions
from utils.cache import cachedRun as cache
from bilibili_api import Verify, user, live, Danmaku
from pathlib import Path

logger = common.getLogger('live')
cfgPath = common.getRunningPath(False) / 'config' / 'live_reply.json'
config = common.loadConfig(cfgPath, logger)
# if config.get('disable', False): raise exceptions.PluginExit('reply', '直播回复')
if config.get('disable', False):
    logger.warning('直播弹幕回复模块已禁用')
conf = {}
verify = common.getVerify()
bot_uid = user.get_self_info(verify = verify).get('mid')
msgCheck = TTLCheck(ttl = 5)
msgQueue = Queue(maxsize = 128)

@modules.live.receiver('reply', 'DANMU_MSG')
async def on_danmu(msg):
    if config.get('disable', False): return
    rid = msg['room_display_id']
    info = msg['data']['info']
    if info[2][0] == bot_uid:
        logger.debug('检测到自己的消息，已忽略')
        return
    text = info[1]
    logger.debug(f'收到{rid}房间的弹幕——{text}')
    rule = Filter(rid, text)
    if rule is None:
        logger.debug('无匹配条件')
        return
    if 'regex' in rule:
        obj = re.match(rule['regex'], text)
        if obj is None: return
        regex = obj.groups()
    else:
        regex = None

    data = {
        'uname': info[2][1],
        'uid': info[2][0],
        'text': text,
        'regex': regex
    }
    if info[3]:
        data['medal']= {
            'name': info[3][1],
            'level': info[3][0],
            'anchor_uname': info[3][2],
            'anchor_uid': info[3][-1],
            'anchor_roomid': info[3][3]
        }
    MSG = rule['reply'].format(**data)
    interval = rule.get('interval', 5)
    for m in MSG.splitlines(False):
        if interval == 0 or msgCheck.check((msg['room_real_id'], m)):
            msgCheck.add((msg['room_real_id'], m), interval)
            await msgQueue.put((msg['room_real_id'], m))
        else:
            logger.debug(f'消息——直播间{msg["room_display_id"]}的消息{m}——发送间隔低于设定值，已忽略')

async def sendMsg():
    if config.get('disable', False): return
    lastSend = time.time()
    interval = config.get('reply_interval', 2)
    while True:
        MSG = await msgQueue.get()
        rid = MSG[0]
        msg = MSG[1]
        now = time.time()
        if now - lastSend < interval:
            await asyncio.sleep(interval)
        lastSend = time.time()
        upinfo = cache(user.get_user_info, cache(live.get_room_play_info, rid, verify=None).get('uid'))
        upname = upinfo.get('name')
        danmu = Danmaku(text = str(msg), mode = 1)
        live.send_danmaku(rid, danmaku = danmu, verify = verify)
        logger.info(f'{upname}的直播间--' + msg + '--已发送')
        msgQueue.task_done()

def getRules(rid):
    global conf
    rid = str(rid)
    if rid in conf: return conf[rid]
    conf[rid] = config.get(rid, {}).get('rules', []) + config.get('global', {}).get('rules', [])
    return conf[rid]

def Filter(rid, text):
    rules = getRules(rid)
    for rule in rules:
        if rule.get('disable', False): continue
        if 'equal' in rule and text != rule['equal']:
            continue
        if 'contain' in rule and text.find(rule['contain']) == -1:
            continue
        if 'startwith' in rule and not text.startswith(rule['startwith']):
            continue
        if 'endwith' in rule and not text.endswith(rule['endwith']):
            continue
        if 'regex' in rule and re.match(rule['regex'], text) is None:
            continue
        return rule
    return None


asyncio.create_task(sendMsg())