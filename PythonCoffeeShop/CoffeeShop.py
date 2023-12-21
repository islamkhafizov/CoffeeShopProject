import sqlite3
from faker import Faker
from datetime import date
import csv

fake = Faker()

conn = sqlite3.connect('coffeeshop.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS customers;')
cursor.execute('DROP TABLE IF EXISTS orders;')
cursor.execute('DROP TABLE IF EXISTS employees;')


cursor.execute('''
    CREATE TABLE customers (
        CustomerID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Address TEXT,
        PhoneNumber TEXT
    )
''')

cursor.execute('''
    CREATE TABLE orders (
        OrderID INTEGER PRIMARY KEY,
        CustomerID INTEGER,
        Description TEXT NOT NULL,
        OrderDate DATE NOT NULL,
        TotalAmount REAL NOT NULL,
        Completed BOOLEAN DEFAULT 0,
        ClerkID INTEGER,
        FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID),
        FOREIGN KEY (ClerkID) REFERENCES employees(EmployeeID)
    )
''')

cursor.execute('''
    CREATE TABLE employees (
        EmployeeID INTEGER PRIMARY KEY,
        Username TEXT NOT NULL,
        Password TEXT NOT NULL,
        Role TEXT NOT NULL
    )
''')

conn.commit()

for _ in range(100):
    cursor.execute("INSERT INTO customers (Name, Address, PhoneNumber) VALUES (?, ?, ?)",
                   (fake.name(), fake.address(), fake.phone_number()))

employees_data = [
    (1, 'clerk', 'qwerty', 'clerk'),
    (2, 'delivery', 'qwerty', 'delivery'),
    (3, 'manager', 'qwerty', 'manager')
]

for employee in employees_data:
    cursor.execute("INSERT INTO employees (EmployeeID, Username, Password, Role) VALUES (?, ?, ?, ?)", employee)


conn.commit()
conn.close()


def login(username, passwd):
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM employees WHERE Username=? AND Password=?", (username, passwd))
    role = cursor.fetchone()
    conn.close()
    return role[0] if role else None


def clerk_menu():
    while True:
        print("\nCRM MENU CLERK")
        print("1. Add order")
        print("2. Add order (new customer)")
        print("3. Assign order to delivery")
        print("4. View pending orders")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            CustomerID = int(input("Enter Customer ID: "))
            Description = input("Enter description: ")
            TotalAmount = int(input("Enter amount: "))
            ClerkID = int(input("Enter Clerk ID: "))
            add_order(CustomerID, Description, TotalAmount, ClerkID)
            print("Order added")
        elif choice == '2':
            Name = input("Enter customer name: ")
            Address = input("Enter customer address: ")
            PhoneNumber = input("Enter customer phone number: ")
            CustomerID = add_new_customer(Name, Address, PhoneNumber)
            Description = input("Enter description: ")
            TotalAmount = int(input("Enter amount: "))
            ClerkID = int(input("Enter Clerk ID: "))
            add_order(CustomerID, Description, TotalAmount, ClerkID)
            print("Order added")
        elif choice == '3':
            OrderID = int(input("Enter order ID: "))
            delivery_employee_id = int(input("Enter delivery employee ID: "))
            assign_order(OrderID, delivery_employee_id)
            print("Order assigned to delivery")
        elif choice == '4':
            view_pending_orders()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again")


def add_new_customer(name, address, phone_number):
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (Name, Address, PhoneNumber) VALUES (?, ?, ?)",
                   (name, address, phone_number))
    customer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return customer_id


def view_pending_orders():
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE Completed=0")
    orders = cursor.fetchall()
    conn.close()
    if not orders:
        print("No pending orders")
    else:
        print("\nPending Orders:")
        for order in orders:
            print(f"Order ID: {order[0]}, Description: {order[2]}, Amount: {order[4]}")


def add_order(customer_id, description, total_amount, clerk_id):
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (CustomerID, Description, OrderDate, TotalAmount, ClerkID) VALUES (?, ?, ?, ?, ?)",
        (customer_id, description, date.today(), total_amount, clerk_id))
    conn.commit()
    conn.close()


def assign_order(order_id, delivery_employee_id):
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET ClerkID=null, Completed=0 WHERE OrderID=?", (order_id,))
    cursor.execute("UPDATE orders SET ClerkID=? WHERE OrderID=?", (delivery_employee_id, order_id))
    conn.commit()
    conn.close()


def delivery_menu():
    while True:
        print("\nCRM MENU DELIVERY")
        print("1. Complete order")
        print("2. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            OrderID = int(input("Enter order ID: "))
            complete_order(OrderID)
            print("Order completed successfully")
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please try again")


def complete_order(order_id):
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET Completed=1 WHERE OrderID=?", (order_id,))
    conn.commit()
    conn.close()


def manager_menu():
    while True:
        print("\nCRM MENU MANAGER")
        print("1. Customer profile")
        print("2. Orders on day")
        print("3. Orders set by clerk")
        print("4. Pending orders")
        print("5. View Customers (export to csv)")
        print("6. View Employees (export to csv)")
        print("7. View Orders (export to csv)")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            customer_profile()
        elif choice == '2':
            orders_on_day()
        elif choice == '3':
            orders_set_by_clerk()
        elif choice == '4':
            view_pending_orders()
        elif choice == '5':
            export_to_csv('customers')
        elif choice == '6':
            export_to_csv('employees')
        elif choice == '7':
            export_to_csv('orders')
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again")


def customer_profile():
    customer_id = int(input("Enter CustomerID: "))
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE CustomerID=?", (customer_id,))
    customer = cursor.fetchone()
    cursor.execute("SELECT COUNT(OrderID), SUM(TotalAmount) FROM orders WHERE CustomerID=?", (customer_id,))
    order_stats = cursor.fetchone()
    conn.close()

    if not customer:
        print("Customer not found")
    else:
        print("\nCustomer Profile:")
        print(f"Customer ID: {customer[0]}, Name: {customer[1]}, Address: {customer[2]}, Phone Number: {customer[3]}")
        print(f"Total Orders: {order_stats[0]}, Amount Paid: {order_stats[1]}")


def orders_on_day():
    order_date = input("Enter date: ")
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE OrderDate=?", (order_date,))
    orders = cursor.fetchall()
    conn.close()
    if not orders:
        print(f"No orders on {order_date}.")
    else:
        print(f"\nOrders on {order_date}:")
        for order in orders:
            print(f"Order ID: {order[0]}, Description: {order[2]}, Amount: {order[4]}")


def orders_set_by_clerk():
    clerk_id = int(input("Enter ClerkID: "))
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE ClerkID=?", (clerk_id,))
    orders = cursor.fetchall()
    conn.close()
    if not orders:
        print(f"No orders set by Clerk {clerk_id}.")
    else:
        print("\nOrders set by Clerk:")
        for order in orders:
            print(f"Order ID: {order[0]}, Description: {order[2]}, Amount: {order[4]}")


def export_to_csv(table_name):
    conn = sqlite3.connect('coffeeshop.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    data = cursor.fetchall()
    conn.close()
    filename = f"{table_name}.csv"
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(data)
    print(f"Data from {table_name} exported to {filename}")


while True:
    print("\nCRM MENU LOGIN")
    username = input("Username: ")
    password = input("Password: ")
    role = login(username, password)
    if role == 'clerk':
        clerk_menu()
    elif role == 'delivery':
        delivery_menu()
    elif role == 'manager':
        manager_menu()
    else:
        print("Wrong username or password. Try again")
