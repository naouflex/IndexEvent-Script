# Event Scanner Script

This Python script scans a specified range of blocks for events emitted by a given Ethereum contract and writes the event data to a CSV file.
Dependencies

This script requires the following Python modules to be installed:

    csv
    argparse
    web3
    dotenv
    os
    json
    time
    tqdm
    requests

The dependencies can be installed using pip:

pip install csv argparse web3 python-dotenv tqdm requests

## Usage

To use the script, run the following command:

php

python event_scanner.py <contract> <event> <start_block>

Where:

    <contract> is the address of the contract to scan.
    <event> is the name of the event to scan for.
    <start_block> is the block number to start scanning from.

The script will scan all blocks between <start_block> and the current block and write the event data to a CSV file with a filename that includes the current timestamp, contract address, event name, start block, and current block.
Environment Variables

This script uses environment variables to set the RPC URL and EtherScan API key. These variables should be set in a .env file in the same directory as the script. The following variables are used:

    RPC_URL: The URL of the Ethereum RPC node to use.
    ETHERSCAN_API_KEY: The API key to use for EtherScan API calls.# IndexEvent-Script
