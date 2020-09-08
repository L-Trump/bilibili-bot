from bilibili_api.exceptions import *

class LoginException(BilibiliApiException):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "登录错误代码：%s, 信息：%s" % (self.code, self.msg)

class ModuleException(Exception):
    pass

class PluginExit(Exception):
    def __init__(self, plugin, plugin_name):
        self.plugin = plugin
        self.plugin_name = plugin_name

    def __str__(self):
        return f"{self.plugin}: {self.plugin_name}停止运行"