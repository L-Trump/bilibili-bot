# 直播回复功能配置

配置文件：/config/live_reply.json

## 配置

- disable: 禁用模块，默认false
- reply_interval: 全局消息回复时间间隔，单位秒（默认:2秒）
- global：全局配置
  - description: 词条描述，请随意配置
  - rules：规则列表，可包含多条规则
    - rule1
    - rule2
- 21403609（直播间ID，单独配置直播间，为数字）
  - 同global

### 规则配置

- rule
  - disable: 禁用当前规则，默认false
  - description: 规则描述
  - **interval: 本条规则的适用时间间隔，即多长时间内不重复使用该规则（防止刷屏），默认5s，单位秒**
  - 以下为具体规则，注意当且仅当所有存在条目均满足时才会被认为匹配，如果想要并列条目请添加多条规则
  - regex: 正则表达式，注意采用match模式，即从第一个字符开始匹配，因此想要匹配中间的文字请自行在前面加入`[\\S\\s]*`，**不要忘记JSON和正则的双重反斜杠转义**
  - contain: 包含文本，当收到的弹幕消息中包含此条目时此条目适用
  - equal: 相等，当收到的弹幕与此条目完全相等时此条目适用
  - startwith: 以xxx开始，当收到的弹幕以此条目为开头时此条目适用
  - endwith: 以xxx结尾，当收到的弹幕以此条目为结尾时此条目适用
  - **reply：本条规则适用时自动回复的消息**
  - **注：除了最基本的文本外，reply词条支持使用扩展格式，见下**

**reply扩展格式：**

- \\n: 即json中的换行格式符，如有换行，消息将会被分为多条发送
- {uname}: 弹幕发送者用户名
- {uid}: 发送者UID
- {text}: 原弹幕文本
- {regex\[\]}: 正则匹配组，仅在规则包含regex条目且包含小组匹配时适用，如`regex[0]``regex[1]`
- {medal\[\]}: 发送者的主播勋章信息组
  - {medal\['name'\]}: 主播勋章名称
  - {medal\['level'\]}: 勋章等级
  - {medal\['anchor_uname'\]}: 勋章所属主播名
  - {medal\['anchor_uid'\]}: 勋章所属主播UID
  - {medal\['anchor_roomid'\]}: 勋章所属主播房间号
