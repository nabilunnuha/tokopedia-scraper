import json, logging, sys, os, csv

def write_csv(data_list: list[dict], filename: str) -> None:
    header = data_list[0].keys()
    mode = 'a' if os.path.exists(filename) else 'w'
    write_header = False if os.path.exists(filename) else True
    with open(filename, mode, newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=header)
        if write_header:
            csv_writer.writeheader()

        csv_writer.writerows(data_list)

def create_logger(logger_name,log_path='./log/log.txt') -> logging.Logger:
    if logger_name not in logging.Logger.manager.loggerDict:

        file_handler = logging.FileHandler(log_path)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger = logging.getLogger(logger_name)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logger = logging.getLogger(logger_name)
        logger.addHandler(console_handler)
        
        logger.setLevel(logging.INFO)

    else:
        logger = logging.getLogger(logger_name)

    return logger

def create_not_exist_folder() -> None:
    if not os.path.exists('results'):
        os.mkdir('results')
    if not os.path.exists('log'):
        os.mkdir('log')
    if not os.path.exists('config'):
        os.mkdir('config')
    if not os.path.exists('config/setting.json'):
        data = {"min_sold": 25, "max_sold":9999, "min_price":25000, "max_price":150000, "min_rating":4.2, 'max_product_per_csv':10000, 'max_page_per_url':99}
        with open('config/setting.json','w') as f:
            json.dump(data,f,indent=4)

def remove_success_scrape(url: str) -> None:
    with open('list_catagori_tokopedia.txt', 'r') as f:
        list_cat = [i.strip() for i in f.readlines()]
        list_cat = [i for i in list(set(list_cat)) if url.strip() != i.strip()]
    
    with open('list_catagori_tokopedia.txt', 'w') as f:
        if list_cat:
            f.write('\n'.join(list_cat))
        else:
            f.write('')
             
from .tokopedia import ColoredFormatter