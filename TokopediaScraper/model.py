from pydantic import BaseModel, HttpUrl
from typing import Optional, Union, List

class Item(BaseModel):
    url: HttpUrl
    name: str
    price: int
    thumbnail_1: Union[HttpUrl, str]
    thumbnail_2: Union[HttpUrl, str]
    thumbnail_3: Union[HttpUrl, str]
    thumbnail_4: Union[HttpUrl, str]
    thumbnail_5: Union[HttpUrl, str]
    thumbnail_6: Union[HttpUrl, str]
    thumbnail_7: Union[HttpUrl, str]
    thumbnail_8: Union[HttpUrl, str]
    thumbnail_9: Union[HttpUrl, str]
    thumbnail_10: Union[HttpUrl, str]
    video: Optional[str] = ''
    description: str
    description_html: Optional[str] = ''
    weight: int
    condition: str
    min_order: int
    category_1: str
    category_2: str
    category_3: str
    category_4: str
    category_5: str
    sold: int
    views: int
    rating: float
    rating_by: int
    stock: int
    size_image: Optional[str] = ''
    
class ProductPage(BaseModel):
    shop_name: str
    product_url: HttpUrl
    price: int
    rating: float
    product_name: str
    identifier_product: str
    shop_domain: str
    
class ItemVariants(BaseModel):
    url: HttpUrl
    v_stock: int
    v_price: int
    v_image: Union[HttpUrl, str]
    v1_name: str
    v1_value: str
    v2_name: str
    v2_value: str