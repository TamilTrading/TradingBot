import logging

from connectors import binance_futures
from interface.root_component import Root

# Setting logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')

# Adding handler to logger
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

public_api = '3185578ea38e712652be579a48efbc81c8c0d2e2469f9d31a364030265ccd4f3'
secret_api = 'b27df2904dfa643bf5b387599cd723e424db4cb17d204f22084952a1a8ac9253'
# bitmex_public_api = 'vaCJMggF0Q1WRNOY3ZPvuSgQ'
# bitmex_secret_api = '6k8xJJEQa2_9BOSUu7o9kgxvxSrCuDMVWAZeCB2xIxy9XD7T'

def main():
    binance_obj = binance_futures.BinanceFuturesClient(public_api, secret_api,
                                                        True)
    root = Root(binance_obj)
    root.mainloop()
    
if __name__ == '__main__':
    main()
