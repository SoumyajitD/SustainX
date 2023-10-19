import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector


df = pd.read_excel('synthetic_data.xlsx')
ingredients_df = pd.read_excel('Ingredients.xlsx')


df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')


df['Holiday'] = df['Holiday'].astype(int)


exog = df[['Mean Weather', 'Holiday']]


train_size = int(0.8 * len(df))
train_data, test_data = df.iloc[:train_size], df.iloc[train_size:]

forecast_steps = len(test_data)

forecast_df = pd.DataFrame()
r2_list = []

for item in ['Margherita Pizza Sold', 'Pepperoni Pizza Sold', 'Cheeseburger Sold', 'Chicken Burger Sold']:
    train_endog = train_data[item]
    test_endog = test_data[item]

   
    model = sm.tsa.ARIMA(train_endog, order=(1, 1, 1), exog=train_data[['Mean Weather', 'Holiday']])
    results = model.fit()

    
    forecast_exog = test_data[['Mean Weather', 'Holiday']]

    
    forecast = results.forecast(steps=forecast_steps, exog=forecast_exog)

    

    forecast_dates = test_data['Date'].values

  
    forecast_df[f'{item} (Forecast)'] = forecast
    forecast_df['Date'] = forecast_dates


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "admin1234567890",
    "database": "store_data"
}


conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()


create_table_query = """
CREATE TABLE IF NOT EXISTS sales_forecast (
    Date DATE,
    Margherita_Pizza_Sold INT,
    Pepperoni_Pizza_Sold INT,
    Cheeseburger_Sold INT,
    Chicken_Burger_Sold INT
)
"""

cursor.execute(create_table_query)


for index, row in forecast_df.iterrows():
    date = row['Date']
    margherita_sales = row['Margherita Pizza Sold (Forecast)']
    pepperoni_sales = row['Pepperoni Pizza Sold (Forecast)']
    cheeseburger_sales = row['Cheeseburger Sold (Forecast)']
    chicken_burger_sales = row['Chicken Burger Sold (Forecast)']

    insert_query = f"""
    INSERT INTO sales_forecast (Date, Margherita_Pizza_Sold, Pepperoni_Pizza_Sold, Cheeseburger_Sold, Chicken_Burger_Sold)
    VALUES ('{date}', {margherita_sales}, {pepperoni_sales}, {cheeseburger_sales}, {chicken_burger_sales})
    """

    cursor.execute(insert_query)


conn.commit()
conn.close()


plt.figure(figsize=(10, 6))
for item in forecast_df.columns:
    if item != 'Date':
        plt.plot(forecast_df['Date'], forecast_df[item], marker='o', label=item)

plt.title('Sales Forecast (Test Set)')
plt.xlabel('Date')
plt.ylabel('Units Sold')
plt.legend()
plt.grid(True)
plt.show()
