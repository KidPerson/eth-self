# <- import the install_solc method!
from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

install_solc("0.6.0")  # <- Add this line and run it at least once

with open("SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# to deploy a contract, you need the bytecode and the ABI

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connectiong to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = os.getenv("PUBLIC_KEY")
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get latestest transaction
nonce = w3.eth.getTransactionCount(my_address)
# Builds transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
# Signs transaction
signed_txn = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)
# Send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# Working with the contract, you always need...
# Contract Address
# Contract ABI

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Call -> simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
# Creates transaction
nonce = w3.eth.getTransactionCount(my_address)
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "gasPrice": w3.eth.gas_price,
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce,
})
# Signs transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
# Sends transaction
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)

# Waits for transaction
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
