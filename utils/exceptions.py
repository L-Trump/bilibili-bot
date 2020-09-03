from bilibili_api.exceptions import *

class LoginException(BilibiliApiException):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "登录错误代码：%s, 信息：%s" % (self.code, self.msg)