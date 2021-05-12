from ecdsa import SigningKey, SECP256k1, VerifyingKey
import hashlib

DIFFICULTY = 8025175753493781531383827216310169394307860406055980532937105502753521

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
    return sha256(str(tx["from"]) + str(tx["to"]) + str(tx["amount"]) + str(tx["time"]))

def sign_tx(tx):
    pass

def verify():
    pass

# sk = SigningKey.generate(curve=SECP256k1)
# vk = sk.verifying_key

# message = bytearray.fromhex(sha256('test'))

# signed = sk.sign(message)

# print(vk.verify(signed, message))



# signature = sk.sign(b"message")
# assert vk.verify(signature, b"message")