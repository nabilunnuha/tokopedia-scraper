import json, time, random, traceback
from TokopediaScraper.other_func import create_not_exist_folder, remove_success_scrape
from TokopediaScraper.tokopedia import Scraper

def main():
    try:
        create_not_exist_folder()
        setting = str(input('default setting ( d / s ) setting ulang: '))
        if setting.lower().strip() == 's':
            min_sold = int(input('min sold: '))
            max_sold = int(input('max sold: '))
            min_price = int(input('min price: '))
            max_price = int(input('max price: '))
            min_rating = float(input('min rating: '))
            max_product_per_csv = int(input('max product per csv: '))
            max_page_per_url = int(input('max page per url: '))
            
            with open('config/setting.json','w') as f:
                data = json.dump({"min_sold": min_sold, "max_sold":max_sold, "min_price":min_price, "max_price":max_price, "min_rating":min_rating, 'max_product_per_csv':max_product_per_csv, 'max_page_per_url':max_page_per_url},
                                 f, indent=4)
        elif setting.lower().strip() == 'd':
            with open('config/setting.json','r') as f:
                data = json.load(f)
            min_sold = data['min_sold']
            max_sold = data['max_sold']
            min_price = data['min_price']
            max_price = data['max_price']
            min_rating = data['min_rating']
            max_product_per_csv = data['max_product_per_csv']
            max_page_per_url = data['max_page_per_url']
        else:
            raise ValueError('Input Salah!')
        generate = str(input('generate category? ( y / n ): '))
        
        scrp = Scraper(
            filter_product={"min_sold": min_sold, "max_sold":max_sold, "min_price":min_price, "max_price":max_price, "min_rating":min_rating},
            max_page_per_url=max_page_per_url,
            )
        log = scrp.logger()
        
        if generate.lower().strip() == 'y' :
            return scrp.generate_category()
        
        data_input_user = {"min_sold": min_sold, "max_sold":max_sold, "min_price":min_price, "max_price":max_price, "min_rating":min_rating, 'max_product_per_csv':max_product_per_csv, 'max_page_per_url':max_page_per_url}
        log.info(f'\n{json.dumps(data_input_user,indent=4)}')
        with open('list_catagori_tokopedia.txt', 'r') as f:
            list_cat = [i.strip() for i in f.readlines()]
            list_cat = list(set(list_cat))
        key_file = random.randint(10000,99999)
        jumlah = 0
        for i in list_cat:
            jum = scrp.scrape(i,key_file)
            jumlah += jum
            if jumlah >= max_product_per_csv:
                key_file = random.randint(10000,99999)
                jumlah = 0
            remove_success_scrape(i)
    except Exception as e:
        exception = str(e)
        error_traceback = traceback.format_exc()
        log.error(f'{exception}\n{error_traceback}')
    finally:
        time.sleep(5)

if __name__ == '__main__':
    main()