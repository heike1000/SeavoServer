import hashlib
import string
from bisect import bisect
import random


# This module has been deprecated

class ConsistentHash:
    def __init__(self, databases, capacities):
        self.ring_database = []
        self.ring_hash = []
        self.databases = databases
        self.capacities = capacities
        for database, capacity in zip(databases, capacities):
            self.add_database(database, capacity)

    def _hash(self, key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % (2 ** 32)

    def add_database(self, database, capacity):
        for i in range(capacity):
            database_virtual = database + "-" + str(i)
            idx = bisect(self.ring_hash, self._hash(database_virtual))
            self.ring_hash.insert(idx, self._hash(database_virtual))
            self.ring_database.insert(idx, database_virtual)

    def get_database_capacity(self, database):
        capacity = sum([1 for i in self.ring_database if database in i])
        return capacity

    def modify_database_capacity(self, database, new_capacity):
        database_count = self.get_database_capacity(database)
        if database_count == new_capacity:
            return
        elif database_count > new_capacity:
            for i in range(database_count - new_capacity):
                database_virtual = database + "-" + str(database_count - i - 1)
                idx = self.ring_database.index(database_virtual)
                del self.ring_database[idx]
                del self.ring_hash[idx]
        else:
            for i in range(new_capacity - database_count):
                database_virtual = database + "-" + str(database_count + i)
                idx = bisect(self.ring_hash, self._hash(database_virtual))
                self.ring_hash.insert(idx, self._hash(database_virtual))
                self.ring_database.insert(idx, database_virtual)

    def remove_database(self, database):
        self.modify_database_capacity(database, 0)

    def get_database(self, key):
        idx = bisect(self.ring_hash, self._hash(key)) % len(self.ring_database)
        database = self.ring_database[idx].split('-')[0]
        return database


if __name__ == "__main__":
    databases = ["devices0", "devices1"]
    capacities = [100, 100]

    consistent_hash = ConsistentHash(databases, capacities)

    device_number = 10000
    SERIAL_NUMBERS = [''.join(random.choices(string.hexdigits.lower(), k=16)) for _ in range(device_number)]
    result = [consistent_hash.get_database(sn) for sn in SERIAL_NUMBERS]

    for db in databases:
        print(f"{db}: {result.count(db)} devices ({result.count(db) / device_number * 100:.2f}%)")
