#imports
from time import sleep
from pymongo import MongoClient
import pprint
from bs4 import BeautifulSoup
from lxml import etree
import requests
from datetime import datetime
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
            'Accept-Language': 'en-US, en;q=0.5'})

date = datetime.today().strftime('%Y-%m-%d')

def convertPrice(price):
    convertedPrice = ""
    for i in price[:price.index(".")]:
        if (i in ['0','1','2','3','4','5','6','7','8','9']):
            convertedPrice += i
    return convertedPrice

def getDetailsFromURL(URL):
    try:
        webpage = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(webpage.content, "html.parser")
        dom = etree.HTML(str(soup))
        
        productTitle = dom.xpath('//*[@id="productTitle"]')[0].text.strip()
        price = dom.xpath('//*[@id="priceblock_ourprice"]')[0].text[2:]
        price = convertPrice(price)
        
        return {'title': productTitle, 'price': price}
    except:
        return None

def connectToDatabase():
    try:
        client = MongoClient()
        db = client.test
        products = db.Products
        return {'client': client, 'products': products}
    except:
        return None

def fetchDataFromDatabase(products, productName, price, URL):
    doc = products.find_one( { 'productName': productName} )
    if(doc):
        doc.get("price").update( {date : int(price)} )
        products.replace_one({ 'productName': doc.get("productName") }, doc )
        priceValues = doc.get("price")
    else:
        new_product = {
            "productName": productName,
            "URL": URL,
            "price":{
                date : int(price)
            }
        }
        products.insert_one(new_product)
        priceValues = products.find_one( { 'productName': productName} ).get("price")
        print("It Seems The Current Product Doesn't Exist In Our Database. Don't worry we have updated it.")
    return priceValues

def updateDatabase(welcomeLabel):
    db = connectToDatabase()
    if(db == None):
        raise DatabaseConnectivityException
    client = db['client']
    products = db['products']
    
    documents = products.find({})
    for doc in documents:
        docURL = doc.get("URL")
        details = getDetailsFromURL(docURL)
        if(details == None):
            doc.get("price").update( {date : 0} )
        else:
            print("Updating Details For Product: " + details['title'] + "\n")
            productName = details['title']
            price = details['price']
            doc.get("price").update( {date : int(price)} )
            products.replace_one({ 'productName': productName }, doc )
        
    client.close()
    print("Database Updation Complete")
    welcomeLabel.configure(text="Database Updating Done ... Enter URL to get price history")
    



def buttonclick(URL, welcomeLabel, root):
    try:
        details = getDetailsFromURL(URL)
        if(details == None):
            raise FetchException
        productName = details['title']
        price = details['price']

        db = connectToDatabase()
        if(db == None):
            raise DatabaseConnectivityException
        client = db['client']
        products = db['products']
        #updateDatabase(products)

        priceValues = fetchDataFromDatabase(products, productName, price, URL)
        
        graphDateValues = list(priceValues.keys())
        graphPriceValues = list(priceValues.values())


        fig = Figure(dpi = 100)
        plt = fig.add_subplot(111)
        plt.plot(graphDateValues, graphPriceValues)
        plt.set_ylim(ymin=0, ymax=graphPriceValues[0]+20000)
        plt.set_title('Price History')
        plt.set_xlabel('Date')
        plt.set_ylabel('Price')
        plt.tick_params(axis='both', which='major', labelsize=7)
        plt.tick_params(axis='x',rotation = 45)
        plt.grid()

        canvas = FigureCanvasTkAgg(fig, master = root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=3, column=0, padx=40, pady=20)
        

    except FetchException:
        welcomeLabel.configure(text="Error Fetching Data From URL", fg="red")
    except DatabaseConnectivityException:
        welcomeLabel.configure(text="Error Connecting To Database", fg="red")
    except FetchFromDatabaseException:
        welcomeLabel.configure(text="Error Fetching Records From Database", fg="red")
    except Exception as e:
        welcomeLabel.configure(text=e, fg="red")


class FetchException(Exception):
    """Raised when there is a problem while fetching data"""
    pass

class DatabaseConnectivityException(Exception):
    """Raised when there is a problem connecting to Database"""
    pass

class FetchFromDatabaseException(Exception):
    """Raised when there is a problem fetching data from a database"""
    pass

def main():    
        root = Tk()
        root.title('Price History')

        welcomeLabel = Label(root, text = "Welcome, Enter the URL to get price history")
        welcomeLabel.grid(row = 0, column = 0, padx = 10, pady = 10)
        inputField = Entry(root, width = 80 , borderwidth = 3)
        inputField.grid(row = 1, column = 0, padx = 10, pady = 10)
        submitButton = Button(root, text = "Submit", width = 20, command = lambda: buttonclick(inputField.get(), welcomeLabel, root))
        submitButton.grid(row = 2, column = 0, padx = 10, pady = 10)
        updateButton = Button(root, text = "Update Database", width = 20, command = lambda: updateDatabase(welcomeLabel))
        updateButton.grid(row = 3, column = 0, padx = 10, pady = 10)
        
        root.mainloop()
       
if __name__ == "__main__":
    main()
