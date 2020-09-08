# 直播间配置

配置文件位置：`/config/live.json`

## 配置

- disable: 禁用live模块，默认: false
- check_interval: 直播间断连检测间隔（单位: 秒），默认：10 
- reconnect_times：直播间断连后尝试重连次数，默认：3
- rooms: 列表，房间配置，见下
  - disable：直播间禁用，默认：false
  - room：房间号（允许列表格式多房间号）
  - plugins: 开启的插件列表，目前支持的插件

## 已支持插件

### 礼物自动感谢

插件代号：gift

插件位置：/modules/live/gift

配置文件位置：/config/live_reply.json

### 关键词自动回复

插件代号：reply

插件位置：/modules/live/reply

配置文件位置：/config/live_reply.json

配置说明：[docs/live_reply.md](/docs/live_reply.md)

## 范例

```json
{
    "disable": false,
    "check_interval": 10,
    "reconnect_times": 3,
    "rooms":[
        {
            "disable": false,
            "room": 21672023,
            "plugins": ["reply"]
        },
        {
            "disable": false,
            "room": [21403609, 21452505, 21696950, 732],
            "plugins": ["gift", "reply"]
        }
    ]
}
```
