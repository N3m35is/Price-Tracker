from pymongo import MongoClient
import pprint
from bs4 import BeautifulSoup
from lxml import etree
import requests
from datetime import datetime


def convertPrice(price):
    convertedPrice = ""
    for i in price[:price.index(".")]:
        if (i in ['0','1','2','3','4','5','6','7','8','9']):
            convertedPrice += i
    return convertedPrice

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})

URL = input("Enter URL for which to get price history\n")

try:
    #Getting Title And Price from the URL
    webpage = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "html.parser")
    dom = etree.HTML(str(soup))
    
    productName = dom.xpath('//*[@id="productTitle"]')[0].text.strip()
    print(productName)
    price = dom.xpath('//*[@id="priceblock_ourprice"]')[0].text[2:]
    price = convertPrice(price)
    print(price)

    #Database Connectivity
    client = MongoClient()
    db = client.test
    products = db.Products
    date = datetime.today().strftime('%Y-%m-%d')

    try:
        doc = products.find_one( { 'productName': productName} )
        if(doc):
            doc.get("price").update( {date : int(price)} )
            products.replace_one({ 'productName': doc.get("productName") }, doc )
            print(doc)
        else:
            new_product = {
                "productName": productName,
                "URL": URL,
                "price":{
                    date : int(price)
                }
            }
            result = products.insert_one(new_product)
            print(result)

    except Exception as e:
        print(e)

    finally:
        client.close()

except Exception as e:
    print(e)


