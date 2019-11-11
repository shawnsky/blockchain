import json
from hashlib import sha256


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, difficulty=3, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = nonce

    def compute_hash(self):
        block_json = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_json.encode()).hexdigest()

    @staticmethod
    def dict2block(b):
        return Block(b['index'],
                     b['transactions'],
                     b['timestamp'],
                     b['previous_hash'],
                     b['difficulty'],
                     b['nonce'])
