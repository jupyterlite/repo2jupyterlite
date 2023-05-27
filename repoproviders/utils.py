from collections import OrderedDict
import time


class Cache(OrderedDict):
    """Basic LRU Cache with get/set"""

    def __init__(self, max_size=1024, max_age=0):
        self.max_size = max_size
        self.max_age = max_age
        self._ages = {}

    def _now(self):
        return time.perf_counter()

    def _check_expired(self, key):
        if not self.max_age:
            return False
        if self._ages[key] + self.max_age < self._now():
            self.pop(key)
            return True
        return False

    def get(self, key, default=None):
        """Get an item from the cache

        same as dict.get
        """
        if key in self and not self._check_expired(key):
            self.move_to_end(key)
        return super().get(key, default)

    def set(self, key, value):
        """Store an item in the cache

        - if already there, moves to the most recent
        - if full, delete the oldest item
        """
        self[key] = value
        self._ages[key] = self._now()
        self.move_to_end(key)
        if len(self) > self.max_size:
            first_key = next(iter(self))
            self.pop(first_key)

    def pop(self, key):
        result = super().pop(key)
        self._ages.pop(key)
        return result
