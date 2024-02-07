import requests, json, time, logging, colorama, re

class Scraper:
    def __init__(self, filter_product:dict, max_page_per_url: int, black_list_key: list[str]) -> None:
        '''
        - ex. filter_product:
            {"min_sold": 10, "max_sold":999,"min_price":10000,"max_price":150000,"min_rating":4.2}
        '''
        self.session = requests.Session()
        self.headers: dict = {
            'content-type': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        }
        self.filter_product: dict = filter_product
        self.max_page_per_url: int = max_page_per_url
        self.black_list_key: list[str] = black_list_key
        self.log: logging = create_logger(__name__)
        self.count_scrape: int = 0
        self.cookie_dict: dict = {}
        self.cookie_list: list = []
        self.timeout: int = 10
        self.warehouse_id: int = 0
        self.shop_id: int = 0
        self.service_type: str = '2h'
        self.addr_id: int = 0
        self.city_id: int = 0
        self.postal_code: str = ''
        self.district_id: int = 0
        self.latlon: str = ''
        self.cat_id_list: list[dict] = self.get_id_category()
        
    def logger(self) -> logging:
        return self.log
        
    def update_cookie(self) -> None:
        result_str_cookie = '; '.join([f'{k}={v}' for k,v in self.cookie_dict.items()])
        self.headers['cookie'] = result_str_cookie
        
    def update_cookie_from_selenium(self) -> None:
        result_str_cookie = '; '.join(['{}={}'.format(i['name'], i['value']) for i in self.cookie_list])
        self.headers['cookie'] = result_str_cookie

    def get_cookies_web_api(self) -> None:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        }
        r = self.session.get('https://www.tokopedia.com/', headers=headers, timeout=self.timeout)
        c_dict = r.cookies.get_dict()
        self.cookie_dict = c_dict
        self.update_cookie()
    
    def upkie(self) -> None:
        r = self.session.get('https://accounts.tokopedia.com/upkie', headers=self.headers, timeout=self.timeout)
        c_response = r.cookies.get_dict()
        self.cookie_dict.update(c_response)
        self.update_cookie()
        
    def GetStateChosenAddress(self) -> None:
        payload = [{"operationName":"GetStateChosenAddress","variables":{"source":"home","is_tokonow_request":True},"query":"query GetStateChosenAddress($source: String!, $is_tokonow_request: Boolean) {\n  keroAddrGetStateChosenAddress(source: $source, is_tokonow_request: $is_tokonow_request) {\n    data {\n      addr_id\n      receiver_name\n      addr_name\n      district\n      city\n      city_name\n      district_name\n      status\n      latitude\n      longitude\n      postal_code\n      __typename\n    }\n    status\n    kero_addr_error {\n      code\n      detail\n      __typename\n    }\n    tokonow {\n      shop_id\n      warehouse_id\n      warehouses {\n        warehouse_id\n        service_type\n        __typename\n      }\n      service_type\n      tokonow_last_update\n      __typename\n    }\n    __typename\n  }\n}\n"}]
        r = self.session.post('https://gql.tokopedia.com/graphql/GetStateChosenAddress', headers=self.headers, data=json.dumps(payload), timeout=self.timeout).json()
        self.warehouse_id: int = r[0]['data']['keroAddrGetStateChosenAddress']['tokonow']['warehouse_id']
        self.shop_id: int = r[0]['data']['keroAddrGetStateChosenAddress']['tokonow']['shop_id']
        self.service_type: str = r[0]['data']['keroAddrGetStateChosenAddress']['tokonow']['service_type']
        self.addr_id: int = r[0]['data']['keroAddrGetStateChosenAddress']['data']['addr_id']
        self.city_id: int = r[0]['data']['keroAddrGetStateChosenAddress']['data']['city']
        self.postal_code: str = r[0]['data']['keroAddrGetStateChosenAddress']['data']['postal_code']
        self.district_id: int = r[0]['data']['keroAddrGetStateChosenAddress']['data']['district']
        self.latlon: str = r[0]['data']['keroAddrGetStateChosenAddress']['data']['latitude'] + r[0]['data']['keroAddrGetStateChosenAddress']['data']['longitude']
        
    def TickerQuery(self) -> None:
        payload = [{"operationName":"TickerQuery","variables":{},"query":"query TickerQuery {\n  ticker {\n    tickers {\n      id\n      title\n      message\n      color\n      type: ticker_type\n      __typename\n    }\n    __typename\n  }\n}\n"}]
        r = self.session.post('https://gql.tokopedia.com/graphql/TickerQuery', headers=self.headers, data=json.dumps(payload), timeout=self.timeout).json()
    
    def get_category_tokopedia(self):
        payload = [{"operationName":"headerMainData","variables":{"filter":"buyer"},"query":"query headerMainData($filter: String) {\n  dynamicHomeIcon {\n    categoryGroup {\n      id\n      title\n      desc\n      categoryRows {\n        id\n        name\n        url\n        imageUrl\n        type\n        categoryId\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  categoryAllListLite(filter: $filter) {\n    categories {\n      id\n      name\n      url\n      iconImageUrl\n      isCrawlable\n      children {\n        id\n        name\n        url\n        isCrawlable\n        children {\n          id\n          name\n          url\n          isCrawlable\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]
        r = self.session.post('https://gql.tokopedia.com/graphql/headerMainData', headers=self.headers, data=json.dumps(payload), timeout=self.timeout).json()
        list_Cat = r[0]['data']['categoryAllListLite']['categories']
        return list_Cat
    
    def hard_refresh(self):
        self.session = requests.Session()
        self.headers: dict = {
            'content-type': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        }
        self.get_cookies_web_api()
        self.upkie()
        self.GetStateChosenAddress()
    
    def get_id_category(self):
        self.hard_refresh()
        list_cat = self.get_category_tokopedia()
        list_result_id: list[dict] = []
        for i in list_cat:
            cid = i['id']
            curl = i['url']
            list_result_id.append({'cid':cid, 'curl':curl})
            if 'children' in i and i['children']:
                for x in i['children']:
                    cid = x['id']
                    curl = x['url']
                    list_result_id.append({'cid':cid, 'curl':curl})
                    if 'children' in x and x['children']:
                        for y in x['children']:
                            cid = y['id']
                            curl = y['url']
                            list_result_id.append({'cid':cid, 'curl':curl})
                            
        return list_result_id
    
    def generate_category(self, output:str='list_catagori_tokopedia.txt') -> None:
        list_result_id: list[str] = [i['curl'] for i in self.cat_id_list]
            
        with open(output,'w') as f:
            f.write('\n'.join(list_result_id))
    
    def get_product_per_category(self,url_category: str) -> list[dict]:
        list_data: list[dict] = []
        try:
            self.restore_headers()
            identifier:str = url_category.split('?')[0]
            url_id = next((f['cid'] for f in self.cat_id_list if identifier.lower() in f['curl'].lower()), None)
            if not url_id:
                raise ValueError('url_id Not found')
            identifier = identifier.replace('https://www.tokopedia.com/p/','').replace('/','_').lower()
            payload = [{"operationName":"SearchProductQuery","variables":{
                "params":f"page=2&ob=&identifier={identifier}&sc={url_id}&user_id=0&rows=60&start=1&source=directory&device=desktop&page=2&related=true&st=product&safe_search=false",
                "adParams":f"page=2&page=2&dep_id={url_id}&ob=&ep=product&item=15&src=directory&device=desktop&user_id=0&minimum_item=15&start=1&no_autofill_range=5-14"
                },"query":"query SearchProductQuery($params: String, $adParams: String) {\n  CategoryProducts: searchProduct(params: $params) {\n    count\n    data: products {\n      id\n      url\n      imageUrl: image_url\n      imageUrlLarge: image_url_700\n      catId: category_id\n      gaKey: ga_key\n      countReview: count_review\n      discountPercentage: discount_percentage\n      preorder: is_preorder\n      name\n      price\n      priceInt: price_int\n      original_price\n      rating\n      wishlist\n      labels {\n        title\n        color\n        __typename\n      }\n      badges {\n        imageUrl: image_url\n        show\n        __typename\n      }\n      shop {\n        id\n        url\n        name\n        goldmerchant: is_power_badge\n        official: is_official\n        reputation\n        clover\n        location\n        __typename\n      }\n      labelGroups: label_groups {\n        position\n        title\n        type\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  displayAdsV3(displayParams: $adParams) {\n    data {\n      id\n      ad_ref_key\n      redirect\n      sticker_id\n      sticker_image\n      productWishListUrl: product_wishlist_url\n      clickTrackUrl: product_click_url\n      shop_click_url\n      product {\n        id\n        name\n        wishlist\n        image {\n          imageUrl: s_ecs\n          trackerImageUrl: s_url\n          __typename\n        }\n        url: uri\n        relative_uri\n        price: price_format\n        campaign {\n          original_price\n          discountPercentage: discount_percentage\n          __typename\n        }\n        wholeSalePrice: wholesale_price {\n          quantityMin: quantity_min_format\n          quantityMax: quantity_max_format\n          price: price_format\n          __typename\n        }\n        count_talk_format\n        countReview: count_review_format\n        category {\n          id\n          __typename\n        }\n        preorder: product_preorder\n        product_wholesale\n        free_return\n        isNewProduct: product_new_label\n        cashback: product_cashback_rate\n        rating: product_rating\n        top_label\n        bottomLabel: bottom_label\n        __typename\n      }\n      shop {\n        image_product {\n          image_url\n          __typename\n        }\n        id\n        name\n        domain\n        location\n        city\n        tagline\n        goldmerchant: gold_shop\n        gold_shop_badge\n        official: shop_is_official\n        lucky_shop\n        uri\n        owner_id\n        is_owner\n        badges {\n          title\n          image_url\n          show\n          __typename\n        }\n        __typename\n      }\n      applinks\n      __typename\n    }\n    template {\n      isAd: is_ad\n      __typename\n    }\n    __typename\n  }\n}\n"
            }]
            r = self.session.post('https://gql.tokopedia.com/graphql/SearchProductQuery',headers=self.headers,data=json.dumps(payload),timeout=self.timeout).json()
            count = r[0]['data']['CategoryProducts']['count']
            max_page = int(count / 60) - 1
            max_page = max_page if max_page <= self.max_page_per_url else self.max_page_per_url
            start = 1
            self.log.info('Getting category product...')
            for page in range(1, max_page):
                try:
                    payload = [{"operationName":"SearchProductQuery","variables":{
                        "params":f"page=2&ob=&identifier={identifier}&sc={url_id}&user_id=0&rows=60&start={start}&source=directory&device=desktop&page=2&related=true&st=product&safe_search=false",
                        "adParams":f"page=2&page=2&dep_id={url_id}&ob=&ep=product&item=15&src=directory&device=desktop&user_id=0&minimum_item=15&start={start}&no_autofill_range=5-14"
                        },"query":"query SearchProductQuery($params: String, $adParams: String) {\n  CategoryProducts: searchProduct(params: $params) {\n    count\n    data: products {\n      id\n      url\n      imageUrl: image_url\n      imageUrlLarge: image_url_700\n      catId: category_id\n      gaKey: ga_key\n      countReview: count_review\n      discountPercentage: discount_percentage\n      preorder: is_preorder\n      name\n      price\n      priceInt: price_int\n      original_price\n      rating\n      wishlist\n      labels {\n        title\n        color\n        __typename\n      }\n      badges {\n        imageUrl: image_url\n        show\n        __typename\n      }\n      shop {\n        id\n        url\n        name\n        goldmerchant: is_power_badge\n        official: is_official\n        reputation\n        clover\n        location\n        __typename\n      }\n      labelGroups: label_groups {\n        position\n        title\n        type\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  displayAdsV3(displayParams: $adParams) {\n    data {\n      id\n      ad_ref_key\n      redirect\n      sticker_id\n      sticker_image\n      productWishListUrl: product_wishlist_url\n      clickTrackUrl: product_click_url\n      shop_click_url\n      product {\n        id\n        name\n        wishlist\n        image {\n          imageUrl: s_ecs\n          trackerImageUrl: s_url\n          __typename\n        }\n        url: uri\n        relative_uri\n        price: price_format\n        campaign {\n          original_price\n          discountPercentage: discount_percentage\n          __typename\n        }\n        wholeSalePrice: wholesale_price {\n          quantityMin: quantity_min_format\n          quantityMax: quantity_max_format\n          price: price_format\n          __typename\n        }\n        count_talk_format\n        countReview: count_review_format\n        category {\n          id\n          __typename\n        }\n        preorder: product_preorder\n        product_wholesale\n        free_return\n        isNewProduct: product_new_label\n        cashback: product_cashback_rate\n        rating: product_rating\n        top_label\n        bottomLabel: bottom_label\n        __typename\n      }\n      shop {\n        image_product {\n          image_url\n          __typename\n        }\n        id\n        name\n        domain\n        location\n        city\n        tagline\n        goldmerchant: gold_shop\n        gold_shop_badge\n        official: shop_is_official\n        lucky_shop\n        uri\n        owner_id\n        is_owner\n        badges {\n          title\n          image_url\n          show\n          __typename\n        }\n        __typename\n      }\n      applinks\n      __typename\n    }\n    template {\n      isAd: is_ad\n      __typename\n    }\n    __typename\n  }\n}\n"
                    }]
                    r = self.session.post('https://gql.tokopedia.com/graphql/SearchProductQuery',headers=self.headers,data=json.dumps(payload),timeout=self.timeout).json()
                    list_product = r[0]['data']['CategoryProducts']['data']
                    start += 60
                    for i in list_product:
                        try:
                            shop_name: str  = i['shop']['name']
                            shop_url: str = i['shop']['url']
                            shop_domain = shop_url.split('/')[-1]
                            product_url: str = i['url']
                            price = int(i['priceInt'])
                            rating = float(i['rating'])
                            product_name: str = i['name']
                            identifier_product: str  = product_url.split('?')[0].replace(f'{shop_url}/','').replace('/','_').lower()
                            
                            if any(key.lower() in clean_string(product_name).lower() for key in self.black_list_key):
                                continue

                            if self.filter_product:
                                if price < self.filter_product['min_price'] or price > self.filter_product['max_price']:
                                    continue
                                if float(rating) < float(self.filter_product['min_rating']):
                                    continue
                            list_data.append({'shop_name':shop_name,'product_url':product_url, 'price':price,'rating':rating,'product_name':product_name,'identifier_product':identifier_product,'shop_domain':shop_domain})
                        except:
                            pass
                except:
                    self.log.error(f'Error: Get product in page {page}')
        except Exception as e:
            self.log.error(f'Error: {e}')
        finally:
            return list_data
    
    def authen_request(self):
        payload = [{"operationName":"isAuthenticatedQuery","variables":{},"query":"query isAuthenticatedQuery {\n  isAuthenticated\n}\n"}]
        self.session.post('https://gql.tokopedia.com/graphql/isAuthenticatedQuery', headers=self.headers, data=json.dumps(payload), timeout=self.timeout).json()
    
    def update_headers_pdp(self):
        h_dict = {
                'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'content-type': 'application/json',
                'accept': '*/*',
                'x-source': 'tokopedia-lite',
                'x-device': 'desktop',
                'x-tkpd-lite-service': 'zeus',
                'x-tkpd-akamai': 'pdpGetLayout',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
            }
        self.headers.update(h_dict)
        
    def restore_headers(self):
        h_dict = {
            'x-source': 'tokopedia-lite',
            'x-tkpd-lite-service': 'zeus',
            'x-tkpd-akamai': 'pdpGetLayout',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
        }
        for i in h_dict:
            if i in self.headers:
                del self.headers[i]
    
    def processing_variant_product(self,url:str,new_variant_options_data: list[dict]) -> list[dict]:
        list_result: list[dict] = []
        childrens = new_variant_options_data[0]['children']
        variants = new_variant_options_data[0]['variants']
        if variants:
            for children in childrens:
                v_stock = children['stock']['stock']
                v_price = children['price']
                v_image = children['picture']['urlOriginal'] if children['picture'] else ''
                v1_name = variants[0]['name']
                v1_value = children['optionName'][0]
                v2_name = variants[1]['name'] if len(variants) > 1 else ''
                v2_value = children['optionName'][1] if len(children['optionName']) > 1 else ''
                result = {'url':url, 'v_stock':v_stock, 'v_price':v_price, 'v_image':v_image, 'v1_name':v1_name, 'v1_value':v1_value, 'v2_name':v2_name, 'v2_value':v2_value}
                list_result.append(result)
                
        return list_result
            
    def get_detail_product(self,shop_domain:str,identifier_product:str) -> tuple[dict,list]:
        try:
            self.upkie()
            self.authen_request()
            payload = [{
                "operationName":"PDPGetLayoutQuery","variables":{
                "shopDomain":str(shop_domain),"productKey":str(identifier_product),"layoutID":"","apiVersion":1,
                "tokonow":{
                    "shopID":str(self.shop_id),"whID":str(self.warehouse_id),"serviceType":str(self.service_type)
                    },
                "deviceID":"",
                "userLocation":{
                    "cityID":str(self.city_id),"addressID":str(self.addr_id),"districtID":str(self.district_id),"postalCode":str(self.postal_code),"latlon":str(self.latlon).strip()
                    },"extParam":"ivf%3Dfalse"},
                "query":"fragment ProductVariant on pdpDataProductVariant {\n  errorCode\n  parentID\n  defaultChild\n  sizeChart\n  totalStockFmt\n  variants {\n    productVariantID\n    variantID\n    name\n    identifier\n    option {\n      picture {\n        urlOriginal: url\n        urlThumbnail: url100\n        __typename\n      }\n      productVariantOptionID\n      variantUnitValueID\n      value\n      hex\n      stock\n      __typename\n    }\n    __typename\n  }\n  children {\n    productID\n    price\n    priceFmt\n    slashPriceFmt\n    discPercentage\n    optionID\n    optionName\n    productName\n    productURL\n    picture {\n      urlOriginal: url\n      urlThumbnail: url100\n      __typename\n    }\n    stock {\n      stock\n      isBuyable\n      stockWordingHTML\n      minimumOrder\n      maximumOrder\n      __typename\n    }\n    isCOD\n    isWishlist\n    campaignInfo {\n      campaignID\n      campaignType\n      campaignTypeName\n      campaignIdentifier\n      background\n      discountPercentage\n      originalPrice\n      discountPrice\n      stock\n      stockSoldPercentage\n      startDate\n      endDate\n      endDateUnix\n      appLinks\n      isAppsOnly\n      isActive\n      hideGimmick\n      isCheckImei\n      minOrder\n      __typename\n    }\n    thematicCampaign {\n      additionalInfo\n      background\n      campaignName\n      icon\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ProductMedia on pdpDataProductMedia {\n  media {\n    type\n    urlOriginal: URLOriginal\n    urlThumbnail: URLThumbnail\n    urlMaxRes: URLMaxRes\n    videoUrl: videoURLAndroid\n    prefix\n    suffix\n    description\n    variantOptionID\n    __typename\n  }\n  videos {\n    source\n    url\n    __typename\n  }\n  __typename\n}\n\nfragment ProductCategoryCarousel on pdpDataCategoryCarousel {\n  linkText\n  titleCarousel\n  applink\n  list {\n    categoryID\n    icon\n    title\n    isApplink\n    applink\n    __typename\n  }\n  __typename\n}\n\nfragment ProductHighlight on pdpDataProductContent {\n  name\n  price {\n    value\n    currency\n    priceFmt\n    slashPriceFmt\n    discPercentage\n    __typename\n  }\n  campaign {\n    campaignID\n    campaignType\n    campaignTypeName\n    campaignIdentifier\n    background\n    percentageAmount\n    originalPrice\n    discountedPrice\n    originalStock\n    stock\n    stockSoldPercentage\n    threshold\n    startDate\n    endDate\n    endDateUnix\n    appLinks\n    isAppsOnly\n    isActive\n    hideGimmick\n    __typename\n  }\n  thematicCampaign {\n    additionalInfo\n    background\n    campaignName\n    icon\n    __typename\n  }\n  stock {\n    useStock\n    value\n    stockWording\n    __typename\n  }\n  variant {\n    isVariant\n    parentID\n    __typename\n  }\n  wholesale {\n    minQty\n    price {\n      value\n      currency\n      __typename\n    }\n    __typename\n  }\n  isCashback {\n    percentage\n    __typename\n  }\n  isTradeIn\n  isOS\n  isPowerMerchant\n  isWishlist\n  isCOD\n  preorder {\n    duration\n    timeUnit\n    isActive\n    preorderInDays\n    __typename\n  }\n  __typename\n}\n\nfragment ProductCustomInfo on pdpDataCustomInfo {\n  icon\n  title\n  isApplink\n  applink\n  separator\n  description\n  __typename\n}\n\nfragment ProductInfo on pdpDataProductInfo {\n  row\n  content {\n    title\n    subtitle\n    applink\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDetail on pdpDataProductDetail {\n  content {\n    title\n    subtitle\n    applink\n    showAtFront\n    isAnnotation\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDataInfo on pdpDataInfo {\n  icon\n  title\n  isApplink\n  applink\n  content {\n    icon\n    text\n    __typename\n  }\n  __typename\n}\n\nfragment ProductSocial on pdpDataSocialProof {\n  row\n  content {\n    icon\n    title\n    subtitle\n    applink\n    type\n    rating\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDetailMediaComponent on pdpDataProductDetailMediaComponent {\n  title\n  description\n  contentMedia {\n    url\n    ratio\n    type\n    __typename\n  }\n  show\n  ctaText\n  __typename\n}\n\nquery PDPGetLayoutQuery($shopDomain: String, $productKey: String, $layoutID: String, $apiVersion: Float, $userLocation: pdpUserLocation, $extParam: String, $tokonow: pdpTokoNow, $deviceID: String) {\n  pdpGetLayout(shopDomain: $shopDomain, productKey: $productKey, layoutID: $layoutID, apiVersion: $apiVersion, userLocation: $userLocation, extParam: $extParam, tokonow: $tokonow, deviceID: $deviceID) {\n    requestID\n    name\n    pdpSession\n    basicInfo {\n      alias\n      createdAt\n      isQA\n      id: productID\n      shopID\n      shopName\n      minOrder\n      maxOrder\n      weight\n      weightUnit\n      condition\n      status\n      url\n      needPrescription\n      catalogID\n      isLeasing\n      isBlacklisted\n      isTokoNow\n      menu {\n        id\n        name\n        url\n        __typename\n      }\n      category {\n        id\n        name\n        title\n        breadcrumbURL\n        isAdult\n        isKyc\n        minAge\n        detail {\n          id\n          name\n          breadcrumbURL\n          isAdult\n          __typename\n        }\n        __typename\n      }\n      txStats {\n        transactionSuccess\n        transactionReject\n        countSold\n        paymentVerified\n        itemSoldFmt\n        __typename\n      }\n      stats {\n        countView\n        countReview\n        countTalk\n        rating\n        __typename\n      }\n      __typename\n    }\n    components {\n      name\n      type\n      position\n      data {\n        ...ProductMedia\n        ...ProductHighlight\n        ...ProductInfo\n        ...ProductDetail\n        ...ProductSocial\n        ...ProductDataInfo\n        ...ProductCustomInfo\n        ...ProductVariant\n        ...ProductCategoryCarousel\n        ...ProductDetailMediaComponent\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
            }]
            self.update_headers_pdp()
            r = self.session.post('https://gql.tokopedia.com/graphql/GetStateChosenAddress', headers=self.headers, data=json.dumps(payload), timeout=self.timeout).json()
            pdpGetLayout = r[0]['data']['pdpGetLayout']
            
            components: list[dict] = pdpGetLayout['components']
            basicInfo: dict = pdpGetLayout['basicInfo']
            url = basicInfo['url']
            sold = int(basicInfo['txStats']['countSold'])
            if sold < int(self.filter_product['min_sold']) or sold > int(self.filter_product['max_sold']):
                return None, None
            new_variant_options_data = [{'children': [], 'variants': []}]
            for component in components:
                if component.get('name') == 'product_content':
                    for data in component.get('data', []):
                        name = data.get('name')
                        price = data.get('price', {}).get('value')
                        stock = data.get('stock', {}).get('value')
                if component.get('name') == 'product_detail':
                    for data in component.get('data', []):
                        description = next((x['subtitle'] for x in data.get('content', []) if x.get('title') == 'Deskripsi'), '')
                        condition = next((x['subtitle'] for x in data.get('content', []) if x.get('title') == 'Kondisi'), None)
                if component.get('name') == 'product_media':
                    product_media_data = component.get('data', [])
                if component.get('name') == 'new_variant_options':
                    new_variant_options_data: list[dict] = component.get('data', [])
            variants = self.processing_variant_product(url,new_variant_options_data)
            pictures = product_media_data[0]['media']
            thumbnail_1 = pictures[0]['urlOriginal'] if len(pictures) >= 1 else ''
            thumbnail_2 = pictures[1]['urlOriginal'] if len(pictures) >= 2 else ''
            thumbnail_3 = pictures[2]['urlOriginal'] if len(pictures) >= 3 else ''
            thumbnail_4 = pictures[3]['urlOriginal'] if len(pictures) >= 4 else ''
            thumbnail_5 = pictures[4]['urlOriginal'] if len(pictures) >= 5 else ''
            thumbnail_6 = pictures[5]['urlOriginal'] if len(pictures) >= 6 else ''
            thumbnail_7 = pictures[6]['urlOriginal'] if len(pictures) >= 7 else ''
            thumbnail_8 = pictures[7]['urlOriginal'] if len(pictures) >= 8 else ''
            thumbnail_9 = pictures[8]['urlOriginal'] if len(pictures) >= 9 else ''
            thumbnail_10 = pictures[9]['urlOriginal'] if len(pictures) >= 10 else ''
            video = ''
            description_html = ''
            weight = basicInfo['weight']
            category_1 = basicInfo['category']['detail'][0]['name'] if len(basicInfo['category']['detail']) >= 1 else ''
            category_2 = basicInfo['category']['detail'][1]['name'] if len(basicInfo['category']['detail']) >= 2 else ''
            category_3 = basicInfo['category']['detail'][2]['name'] if len(basicInfo['category']['detail']) >= 3 else ''
            category_4 = basicInfo['category']['detail'][3]['name'] if len(basicInfo['category']['detail']) >= 4 else ''
            category_5 = basicInfo['category']['detail'][4]['name'] if len(basicInfo['category']['detail']) >= 5 else ''
            views = basicInfo['stats']['countView']
            rating = basicInfo['stats']['rating']
            rating_by = basicInfo['stats']['countReview']
            min_order = basicInfo['minOrder']
            size_image = ''
            result_dict = {
                            "url": url,
                            "name": name,
                            "price": price,
                            "thumbnail_1": thumbnail_1,
                            "thumbnail_2": thumbnail_2,
                            "thumbnail_3": thumbnail_3,
                            "thumbnail_4": thumbnail_4,
                            "thumbnail_5": thumbnail_5,
                            "thumbnail_6": thumbnail_6,
                            "thumbnail_7": thumbnail_7,
                            "thumbnail_8": thumbnail_8,
                            "thumbnail_9": thumbnail_9,
                            "thumbnail_10": thumbnail_10,
                            "video": video,
                            "description": description,
                            "description_html": description_html,
                            "weight": weight,
                            "condition": condition,
                            "min_order": min_order,
                            "category_1": category_1,
                            "category_2": category_2,
                            "category_3": category_3,
                            "category_4": category_4,
                            "category_5": category_5,
                            "sold": sold,
                            "views": views,
                            "rating": rating,
                            "rating_by": rating_by,
                            "stock": stock,
                            "size_image": size_image
                        }
            self.count_scrape += 1
            self.log.info(f'Scraped: {self.count_scrape} product')
            return result_dict, variants
        except Exception as e:
            self.log.error(f'Error: {e}')
            self.log.warning('Sleeping 10s')
            time.sleep(10)
            self.hard_refresh()
            return None, None
        
    def scrape(self,url_category: str,key_output: int) -> int:
        list_data = self.get_product_per_category(url_category)
        self.log.info(f'Found {len(list_data)} product')
        results = []
        variants = []
        for i in list_data:
            result, var = self.get_detail_product(i['shop_domain'], i['identifier_product'])
            if result:
                results.append(result)
            if var:
                variants.extend(var)
                
        if len(results):
            write_csv(results,f'results/products-{key_output}.csv')
            self.log.info(f'Add data: products-{key_output}.csv')
        if len(variants):
            write_csv(variants,f'results/products-{key_output}-variants.csv')
        return len(results)
                   
class ColoredFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        colorama.init()
        super().__init__(*args, **kwargs)
        self._level_colors = {
            logging.INFO: colorama.Fore.GREEN,
            logging.WARNING: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED,
        }
        self._reset_color = colorama.Style.RESET_ALL

    def format(self, record):
        if record.levelno in self._level_colors:
            record.levelname = f"{self._level_colors[record.levelno]}{record.levelname}{self._reset_color}"
        return super().format(record)   
    
from .other_func import create_logger, write_csv, clean_string