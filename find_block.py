from web3 import Web3
from tqdm import tqdm
from threading import Thread, Lock
from multiprocessing import Process, Manager
import math
import time
import os, sys
from dotenv import load_dotenv
load_dotenv()

try:
    # Initialize Web3 provider
    provider = Web3(Web3.HTTPProvider(os.getenv('RPC_URL')))

    # Set contract address
    contract_address = Web3.toChecksumAddress("0x41d5d79431a913c4ae7d69a668ecdfe5ff9dfb68")

    # Set maximum block number to search (currently set to the latest block)
    max_block_number = provider.eth.blockNumber

    # Set number of threads or processes to use
    num_threads_or_processes = 10

    # Set up progress bar with a miniters value of 10
    pbar = tqdm(total=max_block_number, miniters=10)

    # Create a lock for progress bar updates
    pbar_lock = Lock()

    # Define function to search for contract in a range of blocks
    def search_for_contract(start_block, end_block, result_list):
        # Set batch size based on miniters value
        batch_size = pbar.miniters * 10
        for batch_start in range(start_block, end_block + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end_block)
            for block_number in range(batch_start, batch_end + 1):
                # Get block
                block = provider.eth.getBlock(block_number)
                # Loop through transactions in block
                for tx_hash in block['transactions']:
                    # Get transaction receipt
                    tx_receipt = provider.eth.getTransactionReceipt(tx_hash)
                    # Check if contract was created in this transaction
                    if tx_receipt and tx_receipt['contractAddress'] and provider.eth.getCode(tx_receipt['contractAddress']) == provider.eth.getCode(contract_address):
                        # Contract was created in this transaction, so add block number to result list and exit
                        result_list.append(block_number)
                        return
            # Increment the progress bar after each batch of blocks is searched
            with pbar_lock:
                pbar.update(batch_size)

    # Divide the blocks into ranges for each thread or process
    ranges = []
    block_range_size = math.ceil(max_block_number / num_threads_or_processes)

    for i in range(num_threads_or_processes):
        start_block = i * block_range_size
        end_block = min(start_block + block_range_size - 1, max_block_number)
        ranges.append((start_block, end_block))

    # Use multi-threading or multi-processing to search for the contract in multiple blocks at once
    if num_threads_or_processes == 1:
        # Use a single thread
        result_list = []
        search_for_contract(0, max_block_number, result_list)
    else:
        # Use multiple threads or processes
        manager = Manager()
        result_list = manager.list()
        processes = []
        for i in range(num_threads_or_processes):
            start_block, end_block = ranges[i]
            process = Process(target=search_for_contract, args=(start_block, end_block, result_list))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    # Check if contract was found in any block
    if len(result_list) > 0:
        # Contract was found, so
        # Contract was found, so print block number
        print(f"Contract was deployed in block {result_list[0]}")
    else:
        # Contract was not found
        print("Contract not found in any block")

    # Close progress bar
    pbar.close()

except Exception as e:
    print(e)
    print("Error line: ", sys.exc_info()[-1].tb_lineno)
