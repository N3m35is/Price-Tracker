
def convertPrice(price):
    convertedPrice = ""
    for i in price[:price.index(".")]:
        if (i in ['0','1','2','3','4','5','6','7','8','9']):
            convertedPrice += i
    return convertedPrice

print(convertPrice("9797.00"))