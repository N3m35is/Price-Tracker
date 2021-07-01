# Price Tracker
A simple price tracker that can show the price of a product with a given URL.

## Functionality
This is a simple price tracker. Rather than storing price of all products on amazon, it only stores prices of products of which you have viewed price.
Script to update price on daily basis is still in development.

## Usage
Download and install MongoDB and create a database 'test' and a collection 'products'. Commands to do so is given below.
Open Mongo Terminal
1. ```use test```
2. ```db.createCollection('products')```

Download this code as zip and extract it to some path. For example C:\temp\Price-Tracker
Open CMD as admin and run the following command ```cd C:\temp\Price-Tracker```

Now install all dependencies with the following command. Note this is a one-time-step
```pip install -r requirements.txt```

Finally run the script file with the following command
```python final.py```

This assumes you have python 3.9.0 or above already installed. May work with previous version.
