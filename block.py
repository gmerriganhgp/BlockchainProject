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

