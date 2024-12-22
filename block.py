from web3 import Web3
import time
# Connect to Infura
# infura_url = 'https://sepolia.infura.io/v3/9cc2285d9c7243e4b38d456013dfd6d1'
infura_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connected
if not web3.is_connected():
    print("Failed to connect to Infura")
    exit()
    
print("Connected successfully")

# Contract details
private_key = '0x04891ed3985f94d6996ec1f66c8846dcdc96795955ca364a5d2420c49c95cc3c'
# private_key = "b1b6fbf708800811a063d1659e40cd50821fecff2562d5bc4ddb167ae426260d"
# contract_address = '0xabd1b9891021ec2c4f4368f4c18401504d79b060'	
# contract_address="0x8f47de15db3972f1415ebe033bd3331df1566ef9"
contract_address = "0xbce112bd8bea810a2569d4cba86f6759489c4897"
contract_address = Web3.to_checksum_address(contract_address)
contract_abi ='''[
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "examId",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "releaseDate",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "hashcode",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "teacherId",
				"type": "string"
			}
		],
		"name": "storeHash",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "displayCurrentTime",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "examId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "teacherId",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "currentTime",
				"type": "uint256"
			}
		],
		"name": "retrieveHash",
		"outputs": [
			{
				"internalType": "string",
				"name": "hashcode",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "isReleased",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]'''
# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Function to store hash
def store_hash(exam_id, release_date, hashcode, teacher_id):
    account = web3.eth.account.from_key(private_key)
    nonce = web3.eth.get_transaction_count(account.address)

    # Get the current gas price
    current_gas_price = web3.eth.gas_price

    # Set a higher gas price (e.g., 10% more than the current gas price)
    new_gas_price = int(current_gas_price * 1.1)

    # Build transaction
    tx = contract.functions.storeHash(exam_id, release_date, hashcode, teacher_id).build_transaction({
        'chainId': 1337,  # Sepolia chain ID
        'gas': 3000000,
        'gasPrice': new_gas_price,
        'nonce': nonce,
    })

    # Sign transaction
    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
    
    # Send transaction
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f'Transaction sent with hash: {web3.to_hex(tx_hash)}')

    # Wait for the transaction to be mined
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    # Check if the transaction was successful
    if tx_receipt['status'] == 1:
        print("Transaction confirmed successfully.")
    else:
        print("Transaction failed.")


# Function to retrieve hash
def retrieve_hash(exam_id, teacher_id, currentTime):
    result, isReleased = contract.functions.retrieveHash(exam_id, teacher_id, currentTime).call()
    return result, isReleased

# store_hash("m8",1734265983," QmVDmgRcuZ8ZzceAtPmKuiuuLcPVifXBnLVuUR9dkCjUfA","Vasudeva")

m, n = retrieve_hash("m1", "teacher", 1734895183 )
print(m)
print(n)
