
from connectors import binance_connector
import logging
from pprint import pprint

logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

public_api = '3185578ea38e712652be579a48efbc81c8c0d2e2469f9d31a364030265ccd4f3'
secret_api = 'b27df2904dfa643bf5b387599cd723e424db4cb17d204f22084952a1a8ac9253'

def main():
    client_obj = binance_connector.BinanceFuturesClient(public_api, secret_api, \
                                                        True)

if __name__ == '__main__':
    main()