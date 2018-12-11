from collections import defaultdict
from prettytable import PrettyTable
import os
import unittest


def file_reader(file_name, fields_per_line, separator=',', header=False):
    """this generator returns all the values of a line on each call to next()"""
    try:
        fp = open(file_name, 'r') # Do the risky action of attempting to open a file
    except FileNotFoundError:
        print("can't open", file_name) # If file not found, raise exception
    else: # If the file is found
        with fp:
            line_number = 1 # Start line counter to identify line that raises ValueError
            next_line = [] # Initialize next_line variable to store the line in question
            
            for line in fp:
                line = line.rstrip('\n\r').split(separator) # Strips the \n and/or \r from the end of the line and Separates the line into values using the separator
                if len(line) != fields_per_line:
                    raise ValueError(file_name, "has", len(line), "fields in", line_number, "but expected", fields_per_line)
                for value in line: 
                    next_line.append(value)
                
                line = next_line # Transfer the values into line, so we can empty and reuse next_line
                next_line = [] # Before yielding, we must empty next_line for future use
                line_number += 1 # Increase the line counter by 1
                if header == True: # If there is a header, skip that line. 
                    header = False # Set header=False so later lines don't get skipped
                    continue
                yield tuple(line)

class Ecommerce:
    """ Class Ecommerce imports data from .txt files, organizes such data into 
    dictionaries with classes, and prints them in prettytable format """
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.customers = dict()  # self.customers[cust_id] = instance of class Customer
        self.stores = dict()  # self.stores[store_id] = instance of class Store
        # self._products = dict() # self.products[product] = instance of class Product

        # Calls functions that import Ecommerce data from files
        self.import_customers(dir_path)
        self.import_stores(dir_path)
        self.import_products(dir_path)
        self.import_inventory(dir_path)
        self.import_transactions(dir_path)


    # Methods that import data from .txt files, and create instances of classes as values in dicitonaries
    def import_customers(self, dir_path):
        """ Pulls customer data from .txt file and organizes it into the customers dictionary """
        customers_file = os.path.join(dir_path, "customers.txt")
        try:
            for cust_id, name in file_reader(customers_file, 2, ','):
                self.customers[cust_id] = Customer(cust_id, name)
        except ValueError as e:
            print(e)

    def import_stores(self, dir_path):
        """ Pulls store data from .txt file and organizes it into the stores dictionary """
        stores_file = os.path.join(dir_path, "stores.txt")
        try:
            for store_id, name in file_reader(stores_file, 2, '*', True):
                self.stores[store_id] = Store(store_id, name)
        except ValueError as e:
            print(e)

    def import_products(self, dir_path):
        """ reads products from file in dir_path and adds them to a dictionary self._products """
        products_file = os.path.join(dir_path, "products.txt")
        try:
            for product_id, store_id, product_name in file_reader(products_file, 3, separator='|', header=False):
                self.stores[store_id].add_product(product_id) #creates an entry on the products dictionary. For now, qty is zero
        except ValueError as e:
            print(e)        

    def import_inventory(self, dir_path):
        """ reads inventory from file in dir_path and adds them to a dictionary self.inventory """
        products_file = os.path.join(dir_path, "inventory.txt")
        try:
            for store_id, quantity, product_id in file_reader(products_file, 3, separator='|', header=True):
                self.stores[store_id].add_product(product_id, quantity)
        except ValueError as e:
            print(e)

    def import_transactions(self, dir_path):
        """ read the transactions file, update the customer to note the purchase, update store to 
            note the sell. Only sell if item in stock. If customer wants more than whats in stock he will recieve the stock.
        """
        transactions_file = os.path.join(dir_path, "transactions.txt")
        try:
            for cust_id, quantity, product_id, store_id in file_reader(transactions_file, 4, '|', True):
                print("Customer {} wants {} of {}. Store {} has {} in stock. Customer will recieve {}".format(cust_id, quantity, product_id, store_id, self.stores[store_id].products[product_id], min(int(quantity), self.stores[store_id].products[product_id])))
                self.customers[cust_id].buy_product(product_id, min(int(quantity), self.stores[store_id].products[product_id])) # adds dictionary entry pair. See def in class Customer
                self.stores[store_id].sell_product(product_id, min(int(quantity), self.stores[store_id].products[product_id]), cust_id) # adds a customer and product sold in store. See def in Store class.
        except ValueError as e:
            print(e)    


    # Print summary information as tables
    def customer_pt(self):
        """ create a customer pretty table with info the customer and products purchased """
        customer_pt = PrettyTable() # initialize pt
        customer_pt.field_names = Customer.pt_header(self) #set headers as defined in function inside Customer class
        for customer in self.customers.values():
            for row in customer.pt_row():
                customer_pt.add_row(row) # add rows using the output of pt_row defined in Customer class
        return customer_pt

    def store_pt(self):
        """ create a store pretty table with info about sales """
        store_pt = PrettyTable()
        store_pt.field_names = Store.pt_header(self)
        for store in self.stores.values():
            for row in store.pt_row(): #for each list in the set of lists returned by pt_row (each list is a row)
                store_pt.add_row(row) #add it to the pt
        return store_pt

class Customer:
    """ Keeps track of all information concerning customers, 
    including what happens when a customer takes a new course 
    """
    def __init__(self, cust_id, name):
        self.cust_id = cust_id
        self.name = name
        
        self.products = defaultdict(int) #self.products[product] = qty

    def buy_product(self, product_id, quantity):
        """ note that the customer bought a product"""
        self.products[product_id] += int(quantity)
             
    def pt_header(self):
        """ return a list of the fields in the prettytable """
        return ['Customer Name', 'Product', 'Quantity Purchased']

    def pt_row(self):
        """ this generator yields the rows that go into the Customer PrettyTable """
        for product_id, quantity in self.products.items():
            yield [self.name, product_id, quantity]

                
class Store:
    """ Keeps track of all information concerning Stores, 
    including what happens to the store when a customer buys a product 
    """
    def __init__(self, store_id, name):
        self.store_id = store_id
        self.name = name

        self.products = defaultdict(int)  # self.products[product_id] = inventory_qty
        self.sales = defaultdict(lambda: defaultdict(int))

    def add_product(self, product_id, quantity=0):
        """adds products from inventory"""
        self.products[product_id] += int(quantity) #quantity is brought in from the file reader as a string, force it into an int to perform math addition

    def sell_product(self, product_id, quantity, cust_id):
        """ tell the store that a Customer bought a product """
        self.products[product_id] -= int(quantity)
        self.sales[product_id][cust_id] += int(quantity) #keep track of what sold and to who. Necessary for store summary table.

    def pt_header(self):
        return ['Store', 'Products', 'Customers', 'Quantity Sold']

    def pt_row(self):
        """ this generator yields the rows that go into the Store PrettyTable """
        product_qty = 0
        cust_list = []
        for product_id, sales_info in self.sales.items():
            for cust_id, quantity in sales_info.items():
                product_qty += quantity
                cust_list.append(cust_id)
            yield [self.name, product_id, sorted(cust_list), product_qty]
            product_qty = 0
            cust_list = []
        

def main():
    final = Ecommerce('G:\My Drive\F18\SSW-810\FINAL')
    print("Store Summary")
    print(final.store_pt())
    print("Customer Summary")
    print(final.customer_pt())
    

class EcommerceTest(unittest.TestCase):
    def test_customer_instance(self):
        """Tests several customer instances by comparing the values in the instances to the correct values"""
        final = Ecommerce('G:\My Drive\F18\SSW-810\FINAL')
        self.assertEqual(final.customers['c01'].name, "Debugging Dinesh")
        self.assertEqual(final.customers['c03'].name, "GitHub Gus")
        self.assertEqual(final.customers['c01'].products, {'p03': 1, 'p02': 1, 'p01': 6, 'p04': 1, 'p05': 11})
        self.assertEqual(final.customers['c02'].products, {'p03': 0, 'p02': 0, 'p04': 1, 'p05': 4+2+2, 'p06': 1+1+5+1+2+2+4}) # values entered manually to ensure all data is being read

    def test_store_instance(self):
        """Tests several store instances by comparing the values in the instances to the correct values"""
        final = Ecommerce('G:\My Drive\F18\SSW-810\FINAL')
        self.assertEqual(final.stores['s00'].name, "Maha's Movies")
        # self.assertEqual(final.stores['s00'].products, {'p00': 91, 'p01': 27}) # tested inventory before transactions
        self.assertEqual(final.stores['s00'].products, {'p00': 91-4, 'p01': 27-10}) # tests after transaction, sold 4 p00 and 10 p10
        self.assertEqual(final.stores['s01'].name, "Ben's Books")
        self.assertEqual(final.stores['s01'].products, {'p02': 2-1-1, 'p03': 1-1, 'p04': 31-1-1-1})
        self.assertEqual(final.stores['s02'].name, "Dariel's Donuts")
        # self.assertEqual(final.stores['s02'].products, {'p05': 72, 'p06': 100}) # tested inventory before transactions
        self.assertEqual(final.stores['s02'].products, {'p05': 72-25, 'p06': 100-36}) # tests after transaction. Sold 25 of p05 and 36 of p06
        

if __name__ == '__main__':
    unittest.main(exit = False, verbosity = 2)
    main()
    
