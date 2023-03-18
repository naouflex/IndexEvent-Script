import csv
import argparse
from web3 import Web3
from dotenv import load_dotenv
import os
import json
import time
from tqdm import tqdm
import requests

# Load environment variables from .env file
load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser()
parser.add_argument('contract', type=str, help='Contract address')
parser.add_argument('event', type=str, help='Event name')
parser.add_argument('start_block', type=str, help='Start Block')

# Parse arguments
args = parser.parse_args()
args.contract = Web3.toChecksumAddress(args.contract)

# Initialize Web3 provider and contract instance
provider = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))
ABI = requests.get(f"https://api.etherscan.io/api?module=contract&action=getabi&address={args.contract}&apikey={os.getenv('ETHERSCAN_API_KEY')}").json()['result']
contract = provider.eth.contract(address=args.contract, abi=ABI)

# Get block number of contract creation transaction
start_block = int(args.start_block)

# Get current block number
current_block = provider.eth.blockNumber

# Initialize list to store event data
event_data = []

# Set up progress bar
pbar = tqdm(total=current_block-start_block)

# Loop through blocks in increments of 1000 and scan for events
for i in range(start_block, current_block, 1000):
    # Set end block to current block plus 999 to avoid overshooting the end block
    current_end_block = min(i + 999, current_block)
    pbar.set_description(f"Scanning blocks {i}-{current_end_block}")

    # Get all events for the specified event type from the range of blocks
    events = contract.events[args.event]().getLogs(fromBlock=i, toBlock=current_end_block)

    # Add event data to list
    for event in events:
        event_row = [event['blockNumber'], event['transactionHash'].hex(), event['logIndex']] + list(event['args'].values())
        event_data.append(event_row)

        event_keys = [key for key in events[0]['args'] if not key.startswith('_')]

    # Update progress bar with estimated time remaining
    pbar.update(current_end_block - i)

# Close progress bar
pbar.close()

# Generate filename based on current timestamp
filename = f"{int(time.time())}_{args.contract}_{args.event}_{start_block}_{current_block}.csv"

print(events)




# Write event data to CSV
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # Get the keys from the Event Data and use them as the column names
    header = ['Block', 'Transaction Hash', 'Log Index'] + event_keys
    writer.writerow(header)

    # Write the data to the CSV file
    for data in event_data:
        writer.writerow(data)
