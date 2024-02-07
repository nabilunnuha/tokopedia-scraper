import json, logging, sys, os, csv, re

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
            
    if not os.path.exists('config/black_list_keyword.txt'):
        data = ['nota', 'live']
        with open('config/black_list_keyword.txt','w') as f:
            f.write('\n'.join(data))

def remove_success_scrape(url: str) -> None:
    with open('list_catagori_tokopedia.txt', 'r', encoding='utf-8') as f:
        list_cat = [i.strip() for i in f.readlines()]
        list_cat = [i for i in list(set(list_cat)) if url.strip() != i.strip()]
    
    with open('list_catagori_tokopedia.txt', 'w') as f:
        if list_cat:
            f.write('\n'.join(list_cat))
        else:
            f.write('')
             
def clean_string(teks: str) -> str:
    teks_bersih = re.sub(r'[^a-zA-Z0-9\s]', '', teks)
    teks_bersih = re.sub(r'\s+', ' ', teks_bersih)
    return teks_bersih.strip()
             
def get_key_user_input(path_key: str='./config/black_list_keyword.txt', min_len_str: int=4) -> list[str]:
    with open(path_key, 'r', encoding='utf-8') as f:
        data = [clean_string(key) for key in f.readlines()]
        data = [key for key in data if len(key) >= min_len_str]
    return list(set(data))
             
from .tokopedia import ColoredFormatter