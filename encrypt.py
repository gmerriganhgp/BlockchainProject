from ecdsa import SigningKey, SECP256k1
import hashlib

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


def get_keys():
    # returns Private Key, Public Key
    secret = SigningKey.generate(SECP256k1)
    public = secret.verifying_key
    return secret, public

def sign(message, secret_key):
    sk = SigningKey.from_string(secret_key, curve=SECP256k1)
    return sk.sign(bytes(message))

def key_from_string(string):
    return SigningKey.from_string(string, curve=SECP256k1)

def hash_tx(tx):
    return sha256(tx["from"] + tx["to"] + tx["amount"] + tx["timestamp"])

def sign_tx(tx):
    pass

def verify():
    pass
SigningKey
# text = "message"

secret, public = get_keys()
print(secret.to_string())

# signature = sk.sign(b"message")
# assert vk.verify(signature, b"message")