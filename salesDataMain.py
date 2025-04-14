# Joaquin Elizalde

import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plot

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
username = 'postgres'
password = 'j4n11e02'
host = 'localhost'
port = '5433'
database = 'is303'

filePath = 'Retail_Sales_Data.xlsx'

# For visibility
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Get choice from user
iChoice = input('If you want to import data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: ')
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
    engine = sqlalchemy.create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
    df.to_sql("sale", engine, if_exists = 'replace', index = False)

    print("You've imported the excel file into your postgres database")
    print(df)
elif iChoice == '2':
    print("The following are all the categories that have been sold:")
    # Connects to postgres and queries for categories
    engine = sqlalchemy.create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')
    sales = pd.read_sql_query('select distinct category from sale', engine)
    iCatCount = 1
    # Display categories
    for category in sales['category'].values:
        print(f'{iCatCount}: {category}')
        iCatCount += 1
    # Gets the requested category and links it to an option
    sumNum = int(input('PLease enter the number of the category you want to see summarized: '))

    requestedCategory = sales.iloc[sumNum - 1, 0]
    # Query for specific data
    newDf = pd.read_sql_query(f"select product, category, quantity_sold, total_price from sale where category = '{requestedCategory}'", engine)
    
    # Display info for the category
    print(f"Total sales for {requestedCategory}: {newDf['total_price'].sum():,.2f}")
    print(f"Average sale amount for {requestedCategory}: {newDf['total_price'].mean():,.2f}")
    print(f"Total units sold for {requestedCategory}: {newDf['quantity_sold'].sum():,}")

    # Creates and shows bar chart
    # Group by gets one row for each product and calcs sum for each
    dfProductSales = newDf.groupby('product')['total_price'].sum()

    # Create chart and titles
    dfProductSales.plot(kind='bar')
    plot.title(f"Total sales in {requestedCategory}")
    plot.xlabel('Product')
    plot.ylabel('Total Sales')
    # Shows chart on screen
    plot.show()
