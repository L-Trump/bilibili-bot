import modules, re, time
import asyncio
from utils import common
from utils.cache import cachedRun as cache
from bilibili_api import Verify, user, live, Danmaku
from pathlib import Path

logger = common.getLogger('live')
cfgPath = common.getRunningPath(False) / 'config' / 'live_reply.json'
config = common.loadConfig(cfgPath, logger)
conf = {}
verify = common.getVerify()
msgQueue = asyncio.Queue(maxsize = 128)

@modules.live.receiver('reply', 'DANMU_MSG')
async def on_danmu(msg):
    rid = msg['room_display_id']
    info = msg['data']['info']
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
    await msgQueue.put((msg['room_real_id'], MSG))

async def sendMsg():
    lastSend = time.time()
    while True:
        MSG = await msgQueue.get()
        rid = MSG[0]
        msg = MSG[1]
        now = time.time()
        if now - lastSend < 1.5:
            await asyncio.sleep(1)
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