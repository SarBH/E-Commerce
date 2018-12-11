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
        self._products = dict() # self.products[product] = instance of class Product

        # Calls functions that import Ecommerce data from files
        self.import_customers(dir_path)
        self.import_stores(dir_path)
        self.import_transactions(dir_path)
        self.import_products(dir_path)
        

    # Methods that import data from .txt files, and create instances of classes as values in dicitonaries
    def import_customers(self, dir_path):
        """ Pulls customer data from .txt file and organizes it into the customers dictionary """
        customers_file = os.path.join(dir_path, "customers.txt")
        try:
            for cust_id, name in file_reader(customers_file, 2, ','):
                self.customers[cust_id] = Customer(cust_id, name, self._products[product_name])
        except ValueError as e:
            print(e)

    def import_stores(self, dir_path):
        """ Pulls store data from .txt file and organizes it into the stores dictionary """
        stores_file = os.path.join(dir_path, "stores.txt")
        try:
            for store_id, name in file_reader(stores_file, 2, '*'):
                self.stores[store_id] = Store(store_id, name, inventory)
        except ValueError as e:
            print(e)        

    def import_transactions(self, dir_path):
        """ read the transactions file, update the customer to note the purchase, update store to 
            note the sell.
        """
        transactions_file = os.path.join(dir_path, "transactions.txt")
        try:
            for cust_id, quantity, product_id, store_id in file_reader(transactions_file, 4, '|'):
                self.customers[cust_id].buy_product(product_id, quantity) # adds dictionary entry pair. See def in class Customer
                self.stores[store_id].sell_product(product_id) # adds a customer and product sold in store. See def in Store class.
        except ValueError as e:
            print(e)  
  
    def import_products(self, dir_path):
        """ reads products from file in dir_path and adds them to a dictionary self._products """
        products_file = os.path.join(dir_path, "products.txt")
        try:
            for product_id, store_id, description in file_reader(products_file, 3, separator='|', header=False):
                self.stores.products[product_id] #creates an entry on the products dictionary. For now, qty is zero
        except ValueError as e:
            print(e)

    def import_inventory(self, dir_path):
        """ reads inventory from file in dir_path and adds them to a dictionary self.inventory """
        products_file = os.path.join(dir_path, "inventory.txt")
        try:
            for store_id, quantity, product_id in file_reader(products_file, 3, separator='|', header=True):
                self.stores.products[product_id] += quantity
        except ValueError as e:
            print(e)

    # Print summary information as tables
    def customer_pt(self):
        """ create a customer pretty table with info the customer and products """
        customer_pt = PrettyTable() # initialize pt
        customer_pt.field_names = Customer.pt_header(self) #set headers as defined in function inside Customer class
        for customer in self.customers.values():
            customer_pt.add_row(Customer.pt_row()) # add rows using the output of pt_row defined in Customer class
        return customer_pt

    def store_pt(self):
        """ create an store pretty table with info the store and products """
        store_pt = PrettyTable()
        store_pt.field_names = Store.pt_header(self)
        for row in Store.pt_row(self): #for each list in the set of lists returned by pt_row (each list is a row)
            store_pt.add_row(row) #add it to the pt
        return store_pt

    def product_prettytable(self):
        """ create a pretty table containing information of courses associated with products """
        product_prettytable = PrettyTable() # initialize pt
        product_prettytable.field_names = product.pt_header(self) #set headers as defined in function inside Customer class
        for product in self._products.values():
            product_prettytable.add_row(product.pt_row()) # add rows using the output of pt_row defined in Customer class
        return product_prettytable


class Customer:
    """ Keeps track of all information concerning customers, 
    including what happens when a customer takes a new course """
    def __init__(self, cust_id, name, products):
        self.cust_id = cust_id
        self.name = name
        self.products = defaultdict(lambda = 1) #self.products[product] = qty

        # self.courses = dict()  # self.courses[course] = transaction

    def buy_product(self, product_id, quantity):
        """ note that the customer bought a product"""
        self.products[product_id] = quantity
             
    def pt_header(self):
        """ return a list of the fields in the prettytable """
        return ['Customer Name', 'Product', 'Quantity Purchased']

    def pt_row(self):
        """ return the values for the customers pretty table for self """
        qty = self.product.remaining(self.courses)
        return [self.name, self.product_name, qty]
        
            
class Store:
    """ Keeps track of all information concerning Stores, 
    including what happens to the store when a customer buys a product """
    def __init__(self, store_id, name):
        self.store_id = store_id
        self.name = name

        self.products = defaultdict(int)  # self.products[product_id] = inventory_qty

    def sell_product(self, product_id):
        """ tell the store that a Customer bought a product """
        self.products[product_id] -= 1

    def pt_header(self):
        return ['CWID', 'Name', 'Department', 'Course', '#customers']

    def pt_row(self): #new store.pt_row returns 10 lists, each list will be a row
        """ a generator to return the rows with course and number of customers """
        return list(db.execute("""
            select I.CWID, I.Name, I.Dept, G.Course, count(*) as CustomerPerClass 
            FROM HW11_stores I
            join HW11_transactions G
            on I.CWID = G.Instructor_CWID
            group by G.Course"""))
        


class Product:
    """ Track all the information regarding the product, inlcuding its required and elective courses """
    def __init__(self, department, passing=None):
        self._department = department
        self._required = set()
        self._electives = set()
        if passing is None:
            self.passing_transactions = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
        else:
            self.passing_transactions = passing

    def add_product(self, flag, course):
        """ notes another required course or elective """
        if flag.upper() == 'E':
            self._electives.add(course)
        elif flag.upper() == 'R':
            self._required.add(course)
        else:
            raise ValueError(f"Flag {flag} is invalid for course {course}")

    def pt_header(self):
        """ return a list of the fields in the prettytable """
        return ['product', 'Required Courses', 'Elective Courses']

    def pt_row(self):
        """ returns the list of values that populate the prettytable for a specific product """
        return [self._department, self._required, self._electives]

    def remaining(self, courses):
        """ Calculate completed_courses, remaining_required, remaining_electives from 
        a dictionary of course=transaction for a single customer """
        completed_courses = {course for course, transaction in courses.items() if transaction in self.passing_transactions}
        remaining_required = self._required - completed_courses
        if self._electives.intersection(completed_courses):
            remaining_electives = None
        else:
            remaining_electives = self._electives
        return completed_courses, remaining_required, remaining_electives


def main():
    stevens = Ecommerce('G:\My Drive\F18\SSW-810\Week 10')
    print("Customer Summary")
    student_summary = print(stevens.customer_pt())
    print("Store Summary")
    instructor_summary = print(stevens.store_pt())
    print("product Summary")
    product_summary = print(stevens.product_prettytable())


class EcommerceTest(unittest.TestCase):
    def test_student_instance(self):
        """Tests several customer instances by comparing the values in the instances to the correct values"""
        stevens = Ecommerce('G:\My Drive\F18\SSW-810\Week 10')
        self.assertEqual(stevens.customers['10175'].name, "Erickson, D")
        self.assertEqual(stevens.customers['11461'].name, "Wright, U")
        self.assertEqual(stevens.customers['11461'].courses, {'SYS 800': 'A', 'SYS 750': 'A-', 'SYS 611': 'A'})

    def test_instructor_instance(self):
        """Tests several store instances by comparing the values in the instances to the correct values"""
        stevens = Ecommerce('G:\My Drive\F18\SSW-810\Week 10')
        self.assertEqual(stevens.stores['98764'].name, "Feynman, R")
        self.assertEqual(stevens.stores['98765'].name, "Einstein, A")
        self.assertEqual(stevens.stores['98760'].courses, {'SYS 800': 1, 'SYS 750': 1, 'SYS 611': 2, 'SYS 645': 1})

    def test_product_instance(self):
        """ Tests product instances to compare to the correct values """
        stevens = Ecommerce('G:\My Drive\F18\SSW-810\Week 10')
        self.assertEqual(stevens._products['SFEN']._required, {'SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'})
        self.assertEqual(stevens._products['SFEN']._electives, {'CS 501', 'CS 545', 'CS 513'})


if __name__ == '__main__':
    unittest.main(exit = False, verbosity = 2)
    main()
    
