from block import Block
import time
import math


class BlockChain:
    BLOCK_GEN_INTERVAL = 10  # 10 seconds
    DIFFICULTY_ADJUST_INTERVAL = 10  # 10 blocks

    def __init__(self):
        self.blocks = []
        self.__create_genesis_block()

    def __create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "cuc0123456789")
        self.blocks.append(genesis_block)

    @property
    def last_block(self):
        return self.blocks[-1]

    @staticmethod
    def do_a_difficult_work(block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * block.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    @staticmethod
    def is_valid_new_block(new_block, previous_block):
        # 检查索引是否正确
        if previous_block.index + 1 != new_block.index:
            print("Wrong index: " + str(new_block.index))
            return False
        # 检查hash是否正常连接
        elif previous_block.compute_hash() != new_block.previous_hash:
            print("Wrong previous hash: " + new_block.previous_hash)
            return False
        # 检查hash是否是一个正确的proof
        elif not new_block.compute_hash().startswith('0' * new_block.difficulty):
            print("Not a proof: " + new_block.compute_hash())
            return False
        return True

    def is_valid_chain(self, blocks):
        # skip genesis block
        for i in range(1, len(blocks)):
            if not self.is_valid_new_block(blocks[i], blocks[i - 1]):
                return False
        return True

    def get_difficulty(self, blocks):
        last_block = self.last_block
        if last_block.index % self.DIFFICULTY_ADJUST_INTERVAL == 0 and last_block.index != 0:
            return self.get_adjusted_difficulty(last_block, blocks)
        else:
            return last_block.difficulty

    def get_adjusted_difficulty(self, last_block, blocks):
        previous_adjusted_block = blocks[len(blocks) - self.DIFFICULTY_ADJUST_INTERVAL]
        time_expected = self.BLOCK_GEN_INTERVAL * self.DIFFICULTY_ADJUST_INTERVAL
        time_taken = last_block.timestamp - previous_adjusted_block.timestamp

        if time_taken < (time_expected / 2):
            return previous_adjusted_block.difficulty + 1
        elif time_taken > (time_expected * 2):
            return previous_adjusted_block.difficulty - 1
        else:
            return previous_adjusted_block.difficulty

    @staticmethod
    def eval_real_difficulty(blocks):
        tot = 0
        for block in blocks:
            tot += math.pow(2, block.difficulty)
        return tot

    def find_block(self, transaction):
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=[transaction],
                          timestamp=time.time(),
                          previous_hash=last_block.compute_hash(),
                          difficulty=self.get_difficulty(self.blocks))
        proof = self.do_a_difficult_work(new_block)
        print("Find a new block!")
        print("Proof = "+proof)
        self.__add_block(new_block)

        # todo: broadcast
        return new_block

    def __add_block(self, block):
        if self.is_valid_new_block(block, self.last_block):
            self.blocks.append(block)
        else:
            print("New block invalid")

    def replace_chain(self, blocks):
        if self.is_valid_chain(blocks) and self.eval_real_difficulty(self.blocks) < self.eval_real_difficulty(blocks):
            self.blocks = blocks
            return True
            # todo: broadcast
        return False


if __name__ == "__main__":
    if not False:
        print("1")
    print(time.time())
