import asyncio
import time

class Queue(asyncio.Queue):
    def __iter__(self):
        return iter(self._queue)

class TTLCheck(object):
    def __init__(self, ttl: int = 0):
        self.ttl = ttl
        self._dict = {}

    def add(self, obj, ttl: int = -1):
        if ttl == -1: ttl=self.ttl
        self._dict[hash(obj)] = {
            "addTime": time.time(),
            "ttl": ttl
        }

    def check(self, obj):
        return self.isTimeout(obj)

    def isTimeout(self, obj):
        if hash(obj) not in self._dict:
            return True
        item = self._dict[hash(obj)]
        if item["ttl"] == 0: return False
        if item["addTime"] + item["ttl"] < time.time(): return True
        return False

    def pop(self, obj):
        self._dict.pop(hash(obj))
        