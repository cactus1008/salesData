# Joaquin Elizalde, Annie Jaynes, Becca Braatz, Blake Pead, Michael Jones
# This program takes data from an excel file, cleans it up, and allows the user to look at summaries of data

import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plot
from sqlalchemy import create_engine, text

# Dictionary of correct categories
productCategoriesDict = {
        'Camera': 'Technology',
        'Laptop': 'Technology',
        'Gloves': 'Apparel',
        'Smartphone': 'Technology',
        'Watch': 'Accessories',
        'Backpack': 'Accessories',
        'Water Bottle': 'Household Items',
        'T-shirt': 'Apparel',
        'Notebook': 'Stationery',
        'Sneakers': 'Apparel',
        'Dress': 'Apparel',
        'Scarf': 'Apparel',
        'Pen': 'Stationery',
        'Jeans': 'Apparel',
        'Desk Lamp': 'Household Items',
        'Umbrella': 'Accessories',
        'Sunglasses': 'Accessories',
        'Hat': 'Apparel',
        'Headphones': 'Technology',
        'Charger': 'Technology'}

# Info for postgres
# FOR TA: This is the data for one of our databases but you'll want to change it
# (You probably already know that though)
username = 'postgres'
password = 'j4n11e02'
host = 'localhost'
port = '5433'
database = 'is303'

# Engine and connection for postgres
engine = sqlalchemy.create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
conn = engine.connect()

# File path of sales data spreadsheet
filePath = 'Retail_Sales_Data.xlsx'

# For visibility
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

iChoice = "1"
while iChoice in ["1", "2"]:
    # Get choice from user
    iChoice = input('\nIf you want to import data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ')
    if iChoice == '1':
        # Read the file
        df = pd.read_excel(filePath)
        # Split the name col into a first and last name
        splitNames = df['name'].str.split('_', expand=True)
        
        # Removes the original name col
        del df['name']

        # Inserts 2 new columns in place of original name for first and last
        df.insert(1,'last_name', splitNames[1])
        df.insert(1,'first_name', splitNames[0])
        
        # Updates category column to be correct based on product
        df['category'] = df['product'].map(productCategoriesDict)

        # Saves results to a table called 'sale' in Postgres
        df.to_sql("sale", conn, if_exists = 'replace', index = False)

        print("You've imported the excel file into your postgres database")

    elif iChoice == '2':
        print("The following are all the categories that have been sold:")
        # Connects to postgres and queries for categories
        sales = pd.read_sql_query('select distinct category from sale', conn)

        # Creates dictionary to store the categories and their indexes
        catIndexes = {}

        # Displays categories and indexes and stores them in the dictionary
        for iCount, cat in enumerate(sales['category'], start=1):
            print(f"{iCount}: {cat}")
            catIndexes[str(iCount)] = cat

        # Gets the requested option and links it to a category
        catInput = int(input('Please enter the number of the category you want to see summarized: '))
        requestedCategory = catIndexes[str(catInput)]

        # Query for specific data
        query = '''
            SELECT product, total_price, quantity_sold FROM public.sale
            WHERE category = :category
            '''

        # Runs the query through the original database and stores it in the sales database
        sales = pd.read_sql(text(query), conn, params={"category": requestedCategory})
        
        # Display info for the category
        print(f"Total sales for {requestedCategory}: {sales['total_price'].sum():,.2f}")
        print(f"Average sale amount for {requestedCategory}: {sales['total_price'].mean():,.2f}")
        print(f"Total units sold for {requestedCategory}: {sales['quantity_sold'].sum():,}")

        # Creates and shows bar chart
        # Group by gets one row for each product and calcs sum for each
        dfProductSales = sales.groupby('product')['total_price'].sum()

        # Create chart and titles
        dfProductSales.plot(kind='bar')
        plot.title(f"Total sales in {requestedCategory}")
        plot.xlabel('Product')
        plot.ylabel('Total Sales')
        # Shows chart on screen
        plot.show()

    # Closes the program if they select anything other than 1 or 2
    else:
        print("\nClosing the program.")
# Closes the connection to postgres
conn.close()