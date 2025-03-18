import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import altair as alt

# Database connection settings
db_params = {
    "host": "dbnishaaws.c1wuecawins0.ap-south-1.rds.amazonaws.com",
    "database": "postgres",
    "user": "postgres",
    "password": "rootuser",
    "port": "5432"  # Default PostgreSQL port
}

# Establish database connection
@st.cache_resource  # Cache connection for performance
def connect_to_database():
    try:
        conn = psycopg2.connect(**db_params)
        #st.success("Connected to the database!")
        return conn
    except Exception as e:
        st.error("Failed to connect to the database.")
        st.error(f"Error: {e}")
        return None

conn = connect_to_database()

# Streamlit UI
st.title("RETAIL ORDER DATA ANALYSIS")

#Required questions split into two types

GUVI_Provided_queries = {
    "Find the top 10 highest revenue-generating products": 
        'select r2.product_id,sum(r2.sale_price * r2.quantity) as total_revenue from retail2 r2 join retail1 r1 on r2.order_id = r1.order_id group by r2.product_id order by total_revenue desc limit 10;',
    "Find the top 5 cities with the highest profit margins": 
        'select r1.city, avg((r2.profit / r2.sale_price) * 100) as avg_profit_margin from retail1 r1 join retail2 r2 on r1.order_id = r2.order_id where  r2.sale_price > 0  group by r1.city order by avg_profit_margin desc limit 5;',
    "Calculate the total discount given for each category": 
        'select r1.category,sum(r2.discount) as total_discount from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.category order by total_discount desc;',
    "Find the average sale price per product category": 
        'select r1.category,avg(r2.sale_price) as avg_sale_price from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.category;',
    "Find the region with the highest average sale price":
        'select r1.region,avg(r2.sale_price) as highest_avg_sale_price from retail1 r1 join retail2 r2 on r1.order_id = r2.order_id group by r1.region order by highest_avg_sale_price desc limit 1;',
    "Find the total profit per category": 
        'select r1.category,sum(r2.profit) as total_profit from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.category order by total_profit desc;',
    "Identify the top 3 segments with the highest quantity of orders": 
        'select r1.segment,max(r2.quantity) as highest_quantity from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.segment order by highest_quantity desc limit 3;',
    "Determine the average discount percentage given per region": 
        'select r1.region,avg(r2.discount_percent) as avg_discount_percentage from retail1 r1 join retail2 r2  on r1.order_id=r2.order_id group by r1.region order by avg_discount_percentage desc;',
    "Find the product category with the highest total profit": 
        'select r1.category,sum(r2.profit) as total_profit from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.category order by total_profit desc limit 1;',
    "Calculate the total revenue generated per year": 
        'select extract(year from r1.order_date) as year, sum(r2.sale_price * r2.quantity) as total_revenue from retail1 r1 join retail2 r2 on r1.order_id = r2.order_id group by year order by year;',
    }
  
SELF_Provided_queries = {
    "Find the total number of orders placed in each region":
        'select r1.region,count(distinct r1.order_id) as total_no_of_orders from retail1 r1 group by r1.region;',
    "calculate the total revenue generated per product category":
        'select r1.category,sum(r2.sale_price*r2.quantity) as total_revenue from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.category;',
    "list all orders with their corresponding ship mode and total quantity ordered":
        'select r1.order_id,r1.ship_mode,sum(r2.quantity) as total_quantity from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.order_id order by total_quantity desc;',
    "Find the segment with maximum revenue":
        'select r1.segment,sum(r2.sale_price*r2.quantity) as maximum_revenue from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.segment order by maximum_revenue desc limit 1;',
    "Find the total discount given for each ship mode":
        'select r1.ship_mode,sum(r2.discount) as total_discount from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.ship_mode;',
    "Determine the number of unique product sold in each city":
        'select r1.city,count(distinct r2.product_id) as nunique_product from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.city order by nunique_product desc;',
    "Calculate the average profit margin for each product category":
        'select r1.category,avg((r2.profit/r2.sale_price)*100) as avg_profit_margin from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id where r2.sale_price > 0 group by r1.category;',
    "Find the top 3 cities with the highest revenue":
        'select r1.city,sum(r2.sale_price*r2.quantity) as highest_revenue from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.city order by highest_revenue desc limit 1;',
    "Find the total number of orders and total revenue for each country":
        'select r1.country,count(distinct r1.order_id) as total_no_of_orders,sum(r2.sale_price*r2.quantity) as total_revenue from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.country;',
    "list the top profitable products in each category":
        'select r1.category,sum(r2.profit) as total_profit from retail1 r1 join retail2 r2 on r1.order_id=r2.order_id group by r1.category order by total_profit desc;',

}

# Navigation options
nav = st.radio("choose a Query", ["GUVI Provided Queries", "SELF Provided Queries"])

# choosing a Query based on navigation preferences
if nav == "GUVI Provided Queries":
    st.subheader("GUVI Provided Queries")
    query = st.selectbox("choose a query to visualization process:", list(GUVI_Provided_queries.keys()))
    choose_a_query_section = GUVI_Provided_queries
elif nav == "SELF Provided Queries":                                                                           
    st.subheader("SELF Provided Queries")
    query = st.selectbox("choose a query to visualization process:", list(SELF_Provided_queries.keys()))
    choose_a_query_section = SELF_Provided_queries
else:
    query = None

# Execute to visualize choosing query
if query:
    getting_result = run_query(choose_a_query_section[query])
    if getting_result is not None:
        st.dataframe(getting_result)


# Execute to visualize based on choosed query
       
    if query == "Find the top 10 highest revenue-generating products":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Find the top 5 cities with the highest profit margins":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Calculate the total discount given for each category":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Find the average sale price per product category":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query== "Find the region with the highest average sale price":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Find the total profit per category":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Identify the top 3 segments with the highest quantity of orders":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Determine the average discount percentage given per region":
        getting_result = run_query(GUVI_Provided_queries[query])
    elif query == "Find the product category with the highest total profit":
        getting_result = run_query(GUVI_Provided_queries[query])          
    elif query == "Calculate the total revenue generated per year":
        getting_result = run_query(GUVI_Provided_queries[query])    
    elif query == "Find the total number of orders placed in each region":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "calculate the total revenue generated per product category":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "list all orders with their corresponding ship mode and total quantity ordered":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "Find the segment with maximum revenue":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query== "Find the total discount given for each ship mode":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "Determine the number of unique product sold in each city":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "Calculate the average profit margin for each product category":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "Find the top 3 cities with the highest revenue":
        getting_result = run_query(SELF_Provided_queries[query])
    elif query == "Find the total number of orders and total revenue for each country":
        getting_result = run_query(SELF_Provided_queries[query])          
    elif query == "list the top profitable products in each category":
        getting_result = run_query(SELF_Provided_queries[query])    
 

st.text("Thank you")
