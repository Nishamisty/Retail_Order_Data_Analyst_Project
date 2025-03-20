import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import altair as alt
import sqlite3

# Establish database connection
@st.cache_resource  # Cache connection for performance
def load_data():
    df1 = pd.read_csv(r"order.csv")  
    df2 = pd.read_csv(r"product.csv")
    return df1, df2

df1, df2 = load_data()

# Function to execute a query and return the result as a pandas DataFrame
def run_query(query):
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    df1.to_sql("order_data", conn, index=False, if_exists="replace")
    df2.to_sql("product_data", conn, index=False, if_exists="replace")
    if conn is None:
        return None  # Return None if connection failed

    try:
        df_result = pd.read_sql_query(query, conn)
        return df_result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None


#Queries
given_queries ={
    "Top 10 Products by Revenue": """
            SELECT p.product_id, p.sub_category, SUM(o.sale_price) AS revenue 
            FROM product_data p 
            JOIN order_data o ON p.product_id = o.product_id 
            GROUP BY p.product_id 
            ORDER BY revenue DESC 
            LIMIT 10;
        """,
        "Top 5 Cities by Profit Margin": """
            SELECT city, AVG(
                CASE WHEN sale_price = 0 THEN 0 ELSE ((profit / sale_price) * 100) END
            ) AS profit_margin 
            FROM order_data 
            GROUP BY city 
            ORDER BY profit_margin DESC 
            LIMIT 5;
        """,
        "Total Discount by Category": """
            SELECT p.category, SUM(o.discount_price * o.quantity) AS total_discount 
            FROM product_data p 
            JOIN order_data o ON p.product_id = o.product_id 
            GROUP BY p.category;
        """,
        "Average Sale Price by Category": """
            SELECT p.category, AVG(o.sale_price) AS Avg_saleprice 
            FROM order_data o 
            JOIN product_data p ON p.product_id = o.product_id 
            GROUP BY category;
        """,
        "Region with Highest Average Sales": """
            SELECT region, AVG(sale_price) AS avg_sales 
            FROM order_data 
            GROUP BY region 
            ORDER BY avg_sales DESC 
            LIMIT 1;
        """,
        "Total Profit by Category": """
            SELECT p.category, SUM(o.profit) AS total_profit 
            FROM product_data p 
            JOIN order_data o ON p.product_id = o.product_id 
            GROUP BY p.category;
        """,
        "Highest Quantity Sold by Segment": """
            SELECT segment, SUM(quantity) AS highest_quantity  
            FROM order_data 
            GROUP BY segment 
            ORDER BY highest_quantity DESC;
        """,
        "Average Discount by Region": """
            SELECT region, ROUND(AVG(discount_percent), 2) AS avg_discount 
            FROM order_data 
            GROUP BY region;
        """,
        "Most Profitable Category": """
            SELECT p.category, ROUND(SUM(o.profit), 2) AS total_profit 
            FROM product_data p 
            JOIN order_data o ON p.product_id = o.product_id 
            GROUP BY p.category 
            ORDER BY total_profit DESC 
            LIMIT 1;
        """,
        "Annual Revenue": """
            SELECT order_year, ROUND(SUM(sale_price), 2) AS Revenue_per_year 
            FROM order_data 
            GROUP BY order_year;
        """
    }
own_queries ={
       "Identify the top 5 states with the highest total sales revenue, grouped by category":"""
        select o.state, p.product_id,p.category,round(sum(o.sale_price),2) as sale_price
        from order_data o join product_data p on o.product_id=p.product_id group by state,p.product_id
        order by sum(sale_price) desc limit 5;
        """,
        "Calculate the Total Number of Orders, Quantity, and Revenue for Each Product Category":"""
        select p.category,sum(o.order_id) as order_count,o.quantity,round(sum(o.sale_price),2)
        as revenue from product_data p join order_data o on p.product_id=o.product_id group by p.category,o.quantity;
        """,
        "Identify the top 10 products with the highest quantities sold, along with their total revenue and profit":"""
        select p.product_id, p.category, sum(o.quantity) as Total_quantity,
        round(sum(o.sale_price),2) as Revenue, round(sum(o.profit),2) as profit from 
        product_data p join order_data o on p.product_id=o.product_id group by 
        p.product_id order by sum(o.quantity) desc limit 10;
        """,
        "Rank all regions by the total quantity of products sold, including the total number of orders":"""
        select o.region, sum(o.quantity) as total_quantity, count(o.order_id) as order_count,
        rank() over(order by sum(quantity) desc) from order_data o join 
        product_data p on p.product_id=o.product_id group by o.region;
        """,
        "Determine the Top 3 Customers Based on Their Total Profit Contribution":"""
        select segment, round(sum(profit),2) as profit, rank() 
        over(order by sum(profit) desc) from order_data group by segment;
        """,
        "Determine the Average Quantity Ordered Per Product":"""
        select p.sub_category, round(avg(o.quantity),2) as Avg_quantity,
        count(o.order_id) as total_order from product_data p join order_data o on 
        o.product_id=p.product_id group by p.sub_category;
        """,
        "Analysis of Total Revenue Generated by Each Segment":"""
        select segment, round(sum(sale_price),2) as total_revenue 
        from order_Data group by segment;
        """,
        "Calculate the total profit for all regions":"""
        select region, round(sum(profit),2) as Total_profit from order_Data 
        group by region order by sum(profit) desc;
        """,
        "Which state placed the highest quantity of orders, and what was the corresponding shipping mode?":"""
        select state, sum(quantity) as Total_quanity, ship_mode from order_data 
        group by state,ship_mode order by sum(quantity) desc;
        """,
        "Identify the Month with the Highest Revenue":"""
        select order_month, round(sum(sale_price),2) as profit,
        rank() over(order by sum(sale_price) desc) from order_data group 
        by order_month;"""
    }

# Streamlit UI
st.title("Retail Order Data Analysts Project")
st.sidebar.title("Options")

query_type = st.sidebar.radio("Query Type:", ["Given Queries", "Own Queries"])
query_selection = st.selectbox(
    "Select a Query:",
    list(given_queries.keys() if query_type == "Given Queries" else own_queries.keys()),
)

if st.button("Run Query"):
    query = given_queries[query_selection] if query_type == "Given Queries" else own_queries[query_selection]
    try:
        # Execute query and fetch results
        data = run_query(query)
        #st.success("Query executed successfully!")
        st.write(f"### Results for: {query_selection}")
        st.dataframe(data)
        if "product_name" in data.columns and "total_revenue" in data.columns:
           chart = alt.Chart(data).mark_bar().encode(
           x="product_name",
           y="total_revenue",
           color="product_name",
         )
           st.altair_chart(chart, use_container_width=True)

        elif "city" in data.columns and "profit_margin" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="city",
                y="profit_margin",
                color="city",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "category" in data.columns and "total_discount" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="category",
                y="total_discount",
                color="category",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "category" in data.columns and "average_sale_price" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="category",
                y="average_sale_price",
                color="category",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "region" in data.columns and "average_sale_price" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="region",
                y="average_sale_price",
                color="region",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "category" in data.columns and "total_profit" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="category",
                y="total_profit",
                color="category",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "segment" in data.columns and "total_quantity" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="segment",
                y="total_quantity",
                color="segment",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "region" in data.columns and "average_discount_percentage" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="region",
                y="average_discount_percentage",
                color="region",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "year" in data.columns and "total_revenue" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="year",
                y="total_revenue",
                color="year",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "order_id" in data.columns and "total_discount" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="order_id",
                y="total_discount",
                color="order_id",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "order_date" in data.columns and "quantity" in data.columns:
            chart = alt.Chart(data).mark_line().encode(
                x="order_date",
                y="quantity",
                color="order_date",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "order_id" in data.columns and "total_profit" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="order_id",
                y="total_profit",
                color="order_id",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "region" in data.columns and "total_revenue" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="region",
                y="total_revenue",
                color="region",
            )
            st.altair_chart(chart, use_container_width=True)

        elif "avg_list_price" in data.columns and "order_id" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="order_id:N",  # Treat order_id as a nominal variable
                y="avg_list_price:Q",  # Treat avg_list_price as a quantitative variable
                color="order_id:N",
            ).properties(
                title="Average List Price Per Order"
            )
            st.altair_chart(chart, use_container_width=True)

        elif "order_id" in data.columns and "total_quantity" in data.columns:
            top_quantity_orders = data.nlargest(10, "total_quantity")
            chart = alt.Chart(top_quantity_orders).mark_bar().encode(
                x="order_id:N",
                y="total_quantity:Q",
                color="order_id:N",
            ).properties(
                title="Top 10 Orders with Highest Quantity"
            )
            st.altair_chart(chart, use_container_width=True)

        elif "order_id" in data.columns and "total_revenue" in data.columns:
            chart = alt.Chart(data).mark_bar().encode(
                x="order_id:N",
                y="total_revenue:Q",
                color="order_id:N",
            ).properties(
                title="Total Revenue Per Order"
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No suitable data found for visualization.")
        conn.close()
    except Exception as e:
           st.error("Error executing the query.")
           st.error(f"Error: {e}")
