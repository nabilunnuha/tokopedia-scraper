import unittest, os
from TokopediaScraper.tokopedia import Scraper
from TokopediaScraper.other_func import write_csv, create_not_exist_folder, remove_success_scrape
from TokopediaScraper.logger import create_logger

class TestTokopediaModule(unittest.TestCase):
    def test_scraper_instance(self):
        scraper = Scraper({"min_sold": 25, "max_sold":9999, "min_price":25000, "max_price":150000, "min_rating":4.2}, 10)
        scraper.generate_category()
        os.remove('list_catagori_tokopedia.txt')
        self.assertIsInstance(scraper, Scraper)

    def test_create_logger(self):
        logger = create_logger(__name__)
        logger.debug('this logger level info')
        logger.info('this logger level info')
        logger.warning('this logger level warning')
        logger.error('this logger level error')
        logger.critical('this logger level critical')
        self.assertIsNotNone(logger)
        
    def test_create_not_exist_folder(self):
        logger = create_not_exist_folder()
        self.assertIsNone(logger)

    def test_write_csv(self):
        data = [
            {
                "url": 'https://www.tokopedia.com/sillyco/sillyco-silly-up-popular-fit-standing-silicone-storage-sillybag-ocean-blue-kemasan-organik-49608',
                "name": 'Sillyco - Silly-Up Popular Fit - Standing Silicone Storage / Sillybag - Ocean Blue, Kemasan Organik',
                "price": '89000',
                "thumbnail_1": 'thumbnail_1',
                "thumbnail_2": 'thumbnail_2',
                "thumbnail_3": 'thumbnail_3',
                "thumbnail_4": 'thumbnail_4',
                "thumbnail_5": 'thumbnail_5',
                "thumbnail_6": 'thumbnail_6',
                "thumbnail_7": 'thumbnail_7',
                "thumbnail_8": 'thumbnail_8',
                "thumbnail_9": 'thumbnail_9',
                "thumbnail_10": 'thumbnail_10',
                "video": 'video',
                "description": 'Wadah penyimpanan silikon yang dapat berdiri, multifungsi, dan anti tumpah untuk penggunaan sehari-hari Anda.',
                "description_html": 'description_html',
                "weight": 500,
                "condition": 'Baru',
                "min_order": 1,
                "category_1": 'category_1',
                "category_2": 'category_2',
                "category_3": 'category_3',
                "category_4": 'category_4',
                "category_5": 'category_5',
                "sold": 5,
                "views": 12,
                "rating": 4.3,
                "rating_by": 17,
                "stock": 523,
                "size_image": 'size_image'
            } for _ in range(500)
        ]
        path_output = 'test_output.csv'
        write = write_csv(data, path_output)
        self.assertIsNone(write)
        os.remove(path_output)
        
    def test_remove_success_scrape(self):
        remove = remove_success_scrape('https://www.tokopedia.com/p/rumah-tangga/dekorasi')
        self.assertIsNone(remove)
        
if __name__ == '__main__':
    unittest.main()
