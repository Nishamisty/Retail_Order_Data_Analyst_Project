import streamlit as st
import pandas as pd
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
    
    try:
        df_result = pd.read_sql_query(query, conn)
        return df_result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        conn.close()

# Function to generate charts based on the data
def generate_chart(data):
    if "product_name" in data.columns and "total_revenue" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="product_name",
            y="total_revenue",
            color="product_name",
        )
    elif "city" in data.columns and "profit_margin" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="city",
            y="profit_margin",
            color="city",
        )
    elif "category" in data.columns and "total_discount" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category",
            y="total_discount",
            color="category",
        )
    elif "category" in data.columns and "Avg_saleprice" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category",
            y="Avg_saleprice",
            color="category",
        )
    elif "region" in data.columns and "avg_sales" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="region",
            y="avg_sales",
            color="region",
        )
    elif "category" in data.columns and "total_profit" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category",
            y="total_profit",
            color="category",
        )
    elif "segment" in data.columns and "highest_quantity" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="segment",
            y="highest_quantity",
            color="segment",
        )
    elif "region" in data.columns and "avg_discount" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="region",
            y="avg_discount",
            color="region",
        )
    elif "order_year" in data.columns and "Revenue_per_year" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="order_year",
            y="Revenue_per_year",
            color="order_year",
        )
    else:
        return None
    
    return chart

# Queries
given_queries = {
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

own_queries = {
    "Identify the top 5 states with the highest total sales revenue, grouped by category": """
        SELECT o.state, p.product_id, p.category, ROUND(SUM(o.sale_price), 2) AS sale_price
        FROM order_data o 
        JOIN product_data p ON o.product_id = p.product_id 
        GROUP BY state, p.product_id
        ORDER BY SUM(sale_price) DESC 
        LIMIT 5;
    """,
    "Calculate the Total Number of Orders, Quantity, and Revenue for Each Product Category": """
        SELECT p.category, SUM(o.order_id) AS order_count, o.quantity, ROUND(SUM(o.sale_price), 2) AS revenue 
        FROM product_data p 
        JOIN order_data o ON p.product_id = o.product_id 
        GROUP BY p.category, o.quantity;
    """,
    "Identify the top 10 products with the highest quantities sold, along with their total revenue and profit": """
        SELECT p.product_id, p.category, SUM(o.quantity) AS Total_quantity,
        ROUND(SUM(o.sale_price), 2) AS Revenue, ROUND(SUM(o.profit), 2) AS profit 
        FROM product_data p 
        JOIN order_data o ON p.product_id = o.product_id 
        GROUP BY p.product_id 
        ORDER BY SUM(o.quantity) DESC 
        LIMIT 10;
    """,
    "Rank all regions by the total quantity of products sold, including the total number of orders": """
        SELECT o.region, SUM(o.quantity) AS total_quantity, COUNT(o.order_id) AS order_count,
        RANK() OVER(ORDER BY SUM(quantity) DESC) 
        FROM order_data o 
        JOIN product_data p ON p.product_id = o.product_id 
        GROUP BY o.region;
    """,
    "Determine the Top 3 Customers Based on Their Total Profit Contribution": """
        SELECT segment, ROUND(SUM(profit), 2) AS profit, 
        RANK() OVER(ORDER BY SUM(profit) DESC) 
        FROM order_data 
        GROUP BY segment;
    """,
    "Determine the Average Quantity Ordered Per Product": """
        SELECT p.sub_category, ROUND(AVG(o.quantity), 2) AS Avg_quantity,
        COUNT(o.order_id) AS total_order 
        FROM product_data p 
        JOIN order_data o ON o.product_id = p.product_id 
        GROUP BY p.sub_category;
    """,
    "Analysis of Total Revenue Generated by Each Segment": """
        SELECT segment, ROUND(SUM(sale_price), 2) AS total_revenue 
        FROM order_data 
        GROUP BY segment;
    """,
    "Calculate the total profit for all regions": """
        SELECT region, ROUND(SUM(profit), 2) AS Total_profit 
        FROM order_data 
        GROUP BY region 
        ORDER BY SUM(profit) DESC;
    """,
    "Which state placed the highest quantity of orders, and what was the corresponding shipping mode?": """
        SELECT state, SUM(quantity) AS Total_quantity, ship_mode 
        FROM order_data 
        GROUP BY state, ship_mode 
        ORDER BY SUM(quantity) DESC;
    """,
    "Identify the Month with the Highest Revenue": """
        SELECT order_month, ROUND(SUM(sale_price), 2) AS profit,
        RANK() OVER(ORDER BY SUM(sale_price) DESC) 
        FROM order_data 
        GROUP BY order_month;
    """
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
        if data is not None:
            st.write(f"### Results for: {query_selection}")
            st.dataframe(data)
            
            # Generate and display chart
            chart = generate_chart(data)
            if chart:
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("No suitable data found for visualization.")
    except Exception as e:
        st.error(f"Error executing the query: {e}")
