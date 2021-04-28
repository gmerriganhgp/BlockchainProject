from flask import Flask, Response, request, jsonify
from threading import Thread
import requests
import time
import json
import hashlib
import ast
import encrypt
import ecdsa

def read_ledger():
    with open("ledger.json", "r") as ledger:
        return ledger.read()

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


def node_discover_loop(node):
    while True:
        time.sleep(1)
        # print(node.connections)
        node.find_longest_peer()


# class for Node on the p2p network
class Node:
    def __init__(self, port=5050, connections=[], target_file="ledger.json"):
        import socket
        a = socket.gethostbyname(socket.gethostname())
        print(a)
        self.port = port
        self.connections=connections
        self.app = Flask("test")
        self.app.config['SECRET_KEY'] = sha256("secret_key")
        self.started = False
        self.target_file=target_file
        self.ledger = json.load(open(self.target_file, "r"))
        self.unconfirmed_tx = []

        @self.app.route("/", methods=["GET"])
        def index():
            self.connections.append(request.remote_addr)
            print(request.remote_addr)
            return jsonify(self.connections)

        @self.app.route("/full-ledger", methods=["GET"])
        def full_ledger():
            return str(json.load(open(target_file, "r")))

        @self.app.route("/length", methods=["GET"])
        def length():
            return str(len(json.load(open(target_file, "r"))))

        @self.app.route("/write-transaction", methods=["POST"])
        def write_transaction():
            data = request.form
            print(data)
            if "secret_key" in data.keys():
                assert data["from"] == ecdsa.SigningKey.from_string(data["secret_key"], curve=ecdsa.SECP256k1).verifying_key

            else:
                public = ecdsa.VerifyingKey.from_hex(data["from"].encode(), curve=ecdsa.SECP256k1)
                print(public.verify(data["hash"], data["signature"]))
                print("test")

            return "200"

        @self.app.route("/get-keys", methods=["GET"])
        def get_keys():
            secret, public = encrypt.get_keys()
            return {
                "secret": secret.to_string().hex()
            }

        @self.app.route("/add-block", methods=["POST"])
        def add_block():
            # todo
            return "200"

        @self.app.route("/key-balance/<key>")
        def key_balance(key):
            return self.get_key_balance(key)


        self.thread = Thread(target=self.app.run, kwargs={'port': port, 'host': '0.0.0.0'})
        



    def start(self):
        assert not self.started
        self.started = True
        self.thread.start()
        Thread(target=node_discover_loop, kwargs={'node': self}).start()

    def find_longest_peer(self):
        lengths = {}

        for connection in self.connections:
            res = self.request(connection, "/length")
            if res:
                if int(res.text) > len(self.ledger):
                    self.ledger = ast.literal_eval(self.request(connection, "/full-ledger").text)
                                # ^^ json.load would not work

                    self.update_ledger_file()

            else:
                self.connections.remove(connection)




    def request(self, url, endpoint):
        try:
            return requests.get("http://" + url + endpoint)
        except Exception as e:
            print(e)

    def update_ledger_file(self):
        print("\nupdated ledger file\n")
        json.dump(self.ledger, open(self.target_file, "w"), indent=2)

    def get_key_balance(self, key):
        balance = 0
        num_tx = 0
        ledger = json.load(open("ledger.json"))
        for tx in ledger:
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

node = Node()
node.start()

# node2 = Node(port=5051, connections=["127.0.0.1:5050"], target_file="ledger2.json")
# node2.start()
# node.find_longest_peer()


