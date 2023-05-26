import logging, os

logging.basicConfig(level=logging.INFO, filename=f'{os.getcwd()}\\tools\\log\\bot_logging.log', filemode='w',
                    format='%(asctime)s —> %(levelname)s:: %(message)s'
                           ' | FROM <<%(funcName)s>> function in %(pathname)s')
