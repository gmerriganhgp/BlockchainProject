import encrypt

class Block:
    def __init__(self):
        self.transactions = []
        self.hash = self.hash_self()
    
    def verify_txs(self):
        for tx in self.transactions:
            assert encrypt.hash_tx(tx) == tx["hash"]

        return True

    def hash_self(self):
        return encrypt.sha256(str(self.__dict__))

    def __str__(self):
        return str(self.__dict__)

    @staticmethod
    def from_str(string):
        import json
        a = json.loads(string)
        block = Block()
        for block in a:
            block.transactions.append(a)

        return block

    @staticmethod
    def from_dict(dict):
        block = Block()
        for i in dict["transactions"]:
            block.transactions.append(i)
        return block
