#TODO: sort items by product number
#TODO: add printing ability

#!/usr/bin/env python

from Tkinter import *
from tkMessageBox import *
import shelve
import Tkinter as tk    ## Python 2.x
import tkFont
import ttk
import json
import datetime
import requests
import pyrebase
import re

config = {
  "apiKey": "AIzaSyDLc8m8uKQm7eVk15TUkS-al9vLVPoczKQ",
  "authDomain": "stock-otra-mas.firebaseapp.com",
  "databaseURL": "https://stock-otra-mas.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

url = 'https://stock-otra-mas.firebaseio.com/'

shelvename = "inventory.slv"
firebase = pyrebase.initialize_app(config)
class ProductEntry(Frame):
    """Interface for product entry."""
    
    def __init__(self, parent = None):
        self.db = firebase.database()
    
    def createMenu(self):
        """Get all entry boxes and write to inventory database."""
        file = open("D:\Mis Documentos\Downloads\products385043493.csv","r")
        category = ""
        jsonData = {}
        jsonDataStock = {}        
        date = datetime.datetime.now().__str__()
        for line in self.file:
            product, price, other = line.decode("utf-8").split("	")
            if not price :
                category = product
            else :
                jsonDataStock = {"name":  product,
                                 "price": price,
                                 "price_sell": price,
                                 "category": category,
                                 "stock": 0,
                                 "totalSell": 0,
                                 "initial_stock" :0,
                                 "lastupdate": date,
                                 "multiplier": 0
                                 }        
            print jsonDataStock
            jsonToPython = json.loads(json.JSONEncoder().encode(jsonDataStock))
            print jsonToPython
            key = product.encode("utf-8")
            results = db.child("product").child(key).set(jsonToPython)
            #print results
            

    def updateMenu(self, key, record):
        """Opens DB, writes entries, then closes DB."""
        fileSellDaily = open(r'D:\Mis Documentos\Downloads\products385043493.csv',"r")
        date = datetime.datetime.now().__str__()
        for line in fileSellDaily:
            product, price, count, other = line.decode("utf-8").split("	")
            key = product.encode("ascii", "ignore").__str__()
            print key
            doc_ref = self.db.child('product').child(key).get()
            jsonToPython = json.loads(json.JSONEncoder().encode(doc_ref.val()))


            jsonToPython["price"] = price
            jsonToPython["stock"] = int(jsonToPython["stock"]) + count

            resultUpgrade = self.db.child("product").child(key).update(jsonToPython)
            print resultUpgrade
        

    def updateStock(self, key, record):
        """Opens DB, writes entries, then closes DB."""
        fileSellDaily = open(r'D:\Mis Documentos\Downloads\bestSellersPiece.csv',"r")
        date = datetime.datetime.now().__str__()
        for line in fileSellDaily:
            product, count, total, other = line.decode("utf-8").split("	")
            key = product.encode("ascii", "ignore").__str__()
            print key
            doc_ref = self.db.child('product').child(key).get()
            jsonToPython = json.loads(json.JSONEncoder().encode(doc_ref.val()))

            
            m = re.search('J_(/w)*', key)
            print m
            if m :
                print m.group(0)
                self.updateStockBerr( key, count, total, jsonToPython)
   
            
            jsonToPython["stock"] = int(jsonToPython["stock"]) - int(count)
            resultUpgrade = self.db.child("product").child(key).update(jsonToPython)
            print resultUpgrade
        
 
    def updateStockBerr(self, key, count, total, jsonToPython):
        print "----star updateStockBerr"
        # multiplicado
        multi = 0
        jre = re.search('J_(/w)*', key)
        pre = re.search('P_(/w)*', key)
        p1_2re = re.search('/w+2P_(/w)*', key)
        g19re = re.search('/w+9_(/w)*', key)
        g1L =  re.search('G1L_(/w)*', key)
        # multi per liter
        if jre :
            multi = 1
        if g1L :
            multi = 1    
        if pre :
            multi = 0.5
        if p1_2re :
            multi = 0.25    
        if g19re :
            multi = 1,9  

        print multi
        reStyle = re.search('(?<=_)\w+', key)
        style = reStyle.group()
        print   style
        doc_ref = self.db.child('product').child(style).get()
        print doc_ref.val()
        jsonToPython = json.loads(json.JSONEncoder().encode(doc_ref.val()))

        jsonToPython["stock"] = int(jsonToPython["stock"]) - int(count) * multi
        
        resultUpgrade = self.db.child("product").child(style).update(jsonToPython)
        print "---- End updateStockBerr"

    def createDailySell(self):
        """Opens DB, writes entries, then closes DB."""
        self.db.child("product").child("Morty").set(data)


class ProductDisplay(Frame):
    """Interface for product display"""
    
    def __init__(self, parent = None):
        """Create, pack, and bind entry boxes and buttons for product display"""
        
        Frame.__init__(self)
        self.pack()
        
        self.frameHeading = Frame(self)
        self.frameHeading.pack()
        
        self.frameHeadingTitle = Label(self.frameHeading, text = "Current inventory",
            font = ("Arial", "12", "bold"))
        self.frameHeadingTitle.pack()      
        
        #---Database output
        self.showInventoryFrame = Frame(self).pack()
        
        ##Imported table-like multilist box
                                    
        
        #---Inventory display buttons
        self.inventoryBtnFrame = Frame(self).pack()
        self.fetchInven = Button(self.inventoryBtnFrame, text = "Get inventory",
            command = self.getInven)
        self.fetchInven.pack(side = LEFT)
        
        self.modifyInven = Button(self.inventoryBtnFrame, text = "Update listing",
            command = self.changeInven)
        self.modifyInven.pack(side= LEFT)
        
        self.deleteInven = Button(self.inventoryBtnFrame, text = "Delete entry",
            command = self.clearEntry)
        self.deleteInven.pack(side = LEFT)
        
        self.clearInven = Button(self.inventoryBtnFrame, text = "Clear inventory",
            command = self.delInven)
        self.clearInven.pack(side = LEFT)
    
    def getInven(self):
        """Gets products from DB and displays them.
        
        Opens the shelve, loops through each entry, prints the unpacked tuple
        for each record, then closes the shelve."""
        self.listBox.delete(0, END)
        self.productList = shelve.open(shelvename)
        for item in self.productList.keys():
            (self.descrip, self.colors, self.cost, self.price, 
                self.quan) = self.productList[item]    #unpack tuple
            self.listBox.insert(END, (item, self.descrip, self.colors, self.cost,
                self.price, self.quan))
        self.productList.close()
    
    def clearEntry(self):
        """Deletes an entry from the database.
        
        Gets the highlighted selection, makes a list of the the separate words,
        'pops' the product number entry, finds the product number in the shelve,
        deletes the product, then updates the inventory screen."""
        
        ans = askokcancel("Verify delete", "Really remove item?")   #popup window
        if ans:
            self.productList = shelve.open(shelvename)
            self.getSelection = self.listBox.curselection() #get index of selection
            self.selectedEntry = self.listBox.get(self.getSelection)    #get tuple from selection
            (self.productNum, self.descrip, self.colors, self.cost, self.price, 
                self.quan) = self.selectedEntry    #unpack tuple
            self.entry = self.selectedEntry[0]
            del self.productList[self.entry]
            self.productList.close()
            showinfo(title = "Product removed",
                message = "The product has been removed from inventory.")
            self.getInven()

    def changeInven(self):
        """Allows modification of a database entry.
        
        Called by modifyInven Button"""
        
        try:    #see if a selection was made
            self.getSelection = self.listBox.curselection() #get index of selection
            self.selectedEntry = self.listBox.get(self.getSelection)    #get tuple from selection
            (self.prodnum, self.descrip, self.colors, self.cost, self.price, 
                self.quan) = self.selectedEntry    #unpack tuple
            
            #---New 'edit product' window
            self.editWindow = Toplevel()    
            self.editWindow.title("Edit selected entry")
            
            #---Edit product window widgets
            Label(self.editWindow, text = "Product Number").grid(row = 0, column = 0)
            Label(self.editWindow, text = "Description").grid(row = 0, column = 1)
            Label(self.editWindow, text = "Color").grid(row = 0, column = 2)
            Label(self.editWindow, text = "Unit cost").grid(row = 0, column = 3)
            Label(self.editWindow, text = "Sell price").grid(row = 0, column = 4)
            Label(self.editWindow, text = "Quantity").grid(row = 0, column = 5)
            
            self.oldNum = Entry(self.editWindow, name = "prodNum")
            self.oldNum.grid(row = 1, column = 0)
            self.oldDescrip = Entry(self.editWindow, name = "descrip")
            self.oldDescrip.grid(row = 1, column = 1)
            self.oldColor = Entry(self.editWindow, name = "color")
            self.oldColor.grid(row = 1, column = 2)
            self.oldCost = Entry(self.editWindow, name = "cost")
            self.oldCost.grid(row = 1, column = 3)
            self.oldPrice = Entry(self.editWindow, name = "price")
            self.oldPrice.grid(row = 1, column = 4)
            self.oldQuan = Entry(self.editWindow, name = "quan")
            self.oldQuan.grid(row = 1, column = 5)
            
            self.update = Button(self.editWindow, text = "Update product",
                command = self.updateProduct).grid(row = 2, column = 2)
            self.cancel = Button(self.editWindow, text = "Cancel",
                command = self.cancelProduct).grid(row = 2, column = 3) 
           
            #---Edit product data
            self.oldNum.insert(END, self.prodnum)
            self.oldDescrip.insert(END, self.descrip)
            self.oldColor.insert(END, self.colors)
            self.oldCost.insert(END, self.cost)
            self.oldPrice.insert(END, self.price)
            self.oldQuan.insert(END, self.quan)
            
        except TclError:    #tell user to make a selection first
            showerror(title = "Error!", message = "You must make a selection first!")
    
    def updateProduct(self):
        """Change the values of a database entry.
        
        Called by changeInven Button."""
        
        self.productList = shelve.open(shelvename)
        self.oldEntry = self.oldNum.get()
        self.newQuan = self.oldQuan.get()
        self.newCost = self.oldCost.get()
        self.newPrice = self.oldPrice.get()
        self.newRecord = [self.descrip, self.colors,
            self.newCost, self.newPrice, self.newQuan]
        self.productList[self.oldEntry] = self.newRecord
        self.productList.close()
        self.editWindow.destroy()
    
    def cancelProduct(self):
        """Verify canceling of product update."""
        
        self.editWindow.destroy()
    
    def delInven(self):
        """Deletes all entries in database."""
        
        ans = askokcancel("Verify delete", "Really clear inventory?")   #popup window
        if ans: 
            self.productList = shelve.open(shelvename)
            self.productList.clear()
            self.productList.close()
            showinfo(title = "Inventory cleared",
                message = "Your inventory database has been deleted.")          

def main():
    root = Tk()
    entry = ProductEntry(root)
    display = ProductDisplay(root)
    #entry.readEntry()
    entry.updateStock("123","hola")
    display.pack()
    root.mainloop()
    
if __name__ == "__main__":
    main()
