import hashlib
import string
from bisect import bisect
import random


# This module has been deprecated

class ConsistentHash:
    def __init__(self, databases, capacities):
        self.ring_databases = []
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
            self.ring_databases.insert(idx, database_virtual)

    def get_database(self, key):
        idx = bisect(self.ring_hash, self._hash(key)) % len(self.ring_databases)
        database = self.ring_databases[idx].split('-')[0]
        return database

    def data_migration(self, new_databases, new_capacities, sharding_keys):
        new_ring_hash = []
        new_ring_databases = []
        for database, capacity in zip(new_databases, new_capacities):
            for i in range(capacity):
                database_virtual = database + "-" + str(i)
                idx = bisect(new_ring_hash, self._hash(database_virtual))
                new_ring_hash.insert(idx, self._hash(database_virtual))
                new_ring_databases.insert(idx, database_virtual)
        original_result = [self.get_database(sharding_key) for sharding_key in sharding_keys]
        new_result = []
        for i in sharding_keys:
            idx = bisect(new_ring_hash, self._hash(i)) % len(new_ring_databases)
            new_result.append(new_ring_databases[idx].split('-')[0])
        return original_result, new_result


if __name__ == "__main__":
    databases = ['devices0', 'devices1', 'devices2', 'devices3']
    capacities = [240, 240, 240, 240]
    consistent_hash = ConsistentHash(databases, capacities)
    device_number = 40000
    SERIAL_NUMBERS = [''.join(random.choices(string.hexdigits.lower(), k=16)) for _ in range(device_number)]
    result = [consistent_hash.get_database(sn) for sn in SERIAL_NUMBERS]
    for db in databases:
        print(f"{db}: {result.count(db)} devices ({result.count(db) / device_number * 100:.2f}%)")
