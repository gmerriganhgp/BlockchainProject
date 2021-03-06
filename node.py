from flask import Flask, Response, request, jsonify
from threading import Thread
import requests
import time
import json
import hashlib
import ast
import encrypt
import ecdsa
from block import Block

def read_ledger():
    with open("ledger.json", "r") as ledger:
        return ledger.read()

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


def node_discover_loop(node):
    while True:
        time.sleep(node.loop_delay)
        # print(node.connections)
        try:
            node.connections.remove("127.0.0.1")
        except:
            pass
        node.find_longest_peer()
        with open("addresses.txt", "w") as file1:
            file1.write("\n".join(node.connections))


# class for Node on the p2p network
class Node:
    def __init__(self, port=5050, connections=[], target_file="ledger.json", loop_delay=1):
        import socket
        self.address = socket.gethostbyname(socket.gethostname())

        self.port = port
        self.connections=connections
        self.app = Flask("test")
        self.app.config['SECRET_KEY'] = sha256("secret_key")
        self.started = False
        self.target_file=target_file
        self.ledger = json.load(open(self.target_file, "r"))
        self.unconfirmed_tx = []
        self.loop_delay = loop_delay

        # Default route returns other nodes that node is currently connected to
        @self.app.route("/", methods=["GET"])
        def index():
            if (request.remote_addr not in self.connections) and (request.remote_addr != self.address):
                self.connections.append(request.remote_addr)
            print(request.remote_addr)
            return jsonify(self.connections)

        # returns a node's copy of the full ledger
        # TODO: implement hash tree to replace this method
        @self.app.route("/full-ledger", methods=["GET"])
        def full_ledger():
            return str(json.load(open(target_file, "r")))

        # returns the current length of the node's copy of the ledger
        @self.app.route("/length", methods=["GET"])
        def length():
            return str(len(json.load(open(target_file, "r"))))

        # recieves POST request to add transaction to the ledger. 
        @self.app.route("/write-transaction", methods=["POST"])
        def write_transaction():
            # TODO
            data = request.form
            # print(data)
            if "secret_key" in data.keys():
                assert data["from"] == ecdsa.SigningKey.from_string(data["secret_key"], curve=ecdsa.SECP256k1).verifying_key

            else:
                from_key = bytearray.fromhex(data["from"])

                public = ecdsa.VerifyingKey.from_string(from_key, curve=ecdsa.SECP256k1)

                try:
                    assert data["hash"] == encrypt.hash_tx(data)
                    assert public.verify(bytearray.fromhex(data["signature"]), bytearray.fromhex(data["hash"]))
                    self.unconfirmed_tx.append(dict(data))
                    print(self.unconfirmed_tx)
                except Exception as e:
                    print(e)


            return "200"

        @self.app.route("/get-keys", methods=["GET"])
        def get_keys():
            secret, public = encrypt.get_keys()
            return {
                "secret": secret.to_string().hex()
            }

        @self.app.route("/add-block", methods=["POST"])
        def add_block():
            # TODO
            return "200"

        # returns the current balance of a public key/address
        @self.app.route("/key-balance/<key>")
        def key_balance(key):
            return self.get_key_balance(key)


        self.thread = Thread(target=self.app.run, kwargs={'port': port, 'host': '0.0.0.0'})

        @self.app.route("/unconfirmed-tx")
        def unconfirmed_tx():
            return jsonify(self.unconfirmed_tx)
        



    def start(self):
        assert not self.started
        self.started = True
        self.thread.start()
        # start loop which queries connected nodes.
        Thread(target=node_discover_loop, kwargs={'node': self}).start()

    # checks all known peers 
    def find_longest_peer(self):

        for connection in self.connections:
            res = self.request(connection, "/length")
            if res:
                if int(res.text) > len(self.ledger):
                    self.ledger = ast.literal_eval(self.request(connection, "/full-ledger").text)
                                # ^^ json.load would not work

                    self.update_ledger_file()

            else:
                self.connections.remove(connection)

            try:
                peer_connections = json.loads(self.request(connection, "").text)
                for i in peer_connections:
                    if i not in self.connections:
                        self.connections.append(i)
            except Exception as e:
                self.connections.remove(connection)




    # method for making requests to other nodes
    def request(self, url, endpoint):
        try:
            return requests.get("http://" + url + ":5050" + endpoint)
        except Exception as e:
            print(e)
            return "[]"

    def update_ledger_file(self):
        print("\nupdated ledger file\n")
        json.dump(self.ledger, open(self.target_file, "w"), indent=2)

    def get_key_balance(self, key):
        balance = 0
        num_tx = 0
        ledger = json.load(open("ledger.json"))
        for block in ledger:
            for tx in block["transactions"]:
                if tx["to"] == key:
                    balance += tx["amount"]
                    num_tx += 1

                if tx["from"] == key:
                    balance -= tx["amount"]
                    num_tx += 1

        return {
            "address": key,
            "balance": round(balance, 3),
            "total_transactions": num_tx
        }




# node1 = Node(connections=["127.0.0.1:5051"])
# node1.start()



# node2 = Node(port=5051, connections=["127.0.0.1:5050"], target_file="ledger2.json")
# node2.start()
# node.find_longest_peer()


class MiningNode(Node):

    
    def collect_tx(self):

        for connection in self.connections:
            data = self.request(connection, "/unconfirmed-tx")
            for tx in data:
                if not any(i["hash"] == tx["hash"] for i in self.unconfirmed_tx):
                    self.connections.append(tx)


    def start(self):
        try:
            with open("addresses.txt", "r") as file1:
                for line in file1:
                    self.connections.append(line)

        except:
            pass

        super().start()
        while True:
            self.collect_tx()
            time.sleep(1)



    

