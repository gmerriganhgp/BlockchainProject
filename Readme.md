# Blockchain Project

Blockchain that uses the Flask python library to establish a Peer to Peer network which will reach consensus on a ledger of transactions. 
The ledger is stored in JSON format in the ledger.json file. 

# Transaction shape:
```
{
    "from": address,
    "to": address,
    "amount": float,
    "time": unix timestamp,
    "hash": sha256(str(from) + str(to) + str(amount) + str(time))
    "signature": secret_key.sign(id)
}
```

## Todo:
- [x] Run Flask server in separate thread
- [x] Write Method to update ledger to the longest ledger available
- [x] Write methods for creating public/private key pair and signing transactions
- [ ] Implement node discovery algorithm
- [ ] Implement proof of work algorithm and block hash tree data structure. 
