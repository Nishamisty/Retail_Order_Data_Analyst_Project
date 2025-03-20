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
def generate_chart(data, query_name):
    if "revenue" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="product_id:N",
            y="revenue:Q",
            color="sub_category:N",
            tooltip=["product_id", "sub_category", "revenue"]
        ).properties(
            title=f"{query_name} - Revenue by Product"
        )
    elif "profit_margin" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="city:N",
            y="profit_margin:Q",
            color="city:N",
            tooltip=["city", "profit_margin"]
        ).properties(
            title=f"{query_name} - Profit Margin by City"
        )
    elif "total_discount" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category:N",
            y="total_discount:Q",
            color="category:N",
            tooltip=["category", "total_discount"]
        ).properties(
            title=f"{query_name} - Total Discount by Category"
        )
    elif "Avg_saleprice" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category:N",
            y="Avg_saleprice:Q",
            color="category:N",
            tooltip=["category", "Avg_saleprice"]
        ).properties(
            title=f"{query_name} - Average Sale Price by Category"
        )
    elif "avg_sales" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="region:N",
            y="avg_sales:Q",
            color="region:N",
            tooltip=["region", "avg_sales"]
        ).properties(
            title=f"{query_name} - Average Sales by Region"
        )
    elif "total_profit" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category:N",
            y="total_profit:Q",
            color="category:N",
            tooltip=["category", "total_profit"]
        ).properties(
            title=f"{query_name} - Total Profit by Category"
        )
    elif "highest_quantity" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="segment:N",
            y="highest_quantity:Q",
            color="segment:N",
            tooltip=["segment", "highest_quantity"]
        ).properties(
            title=f"{query_name} - Highest Quantity by Segment"
        )
    elif "avg_discount" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="region:N",
            y="avg_discount:Q",
            color="region:N",
            tooltip=["region", "avg_discount"]
        ).properties(
            title=f"{query_name} - Average Discount by Region"
        )
    elif "Revenue_per_year" in data.columns:
        chart = alt.Chart(data).mark_line().encode(
            x="order_year:N",
            y="Revenue_per_year:Q",
            color=alt.value("blue"),
            tooltip=["order_year", "Revenue_per_year"]
        ).properties(
            title=f"{query_name} - Annual Revenue"
        )
    elif "sale_price" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="state:N",
            y="sale_price:Q",
            color="category:N",
            tooltip=["state", "category", "sale_price"]
        ).properties(
            title=f"{query_name} - Sales Revenue by State and Category"
        )
    elif "order_count" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="category:N",
            y="order_count:Q",
            color="category:N",
            tooltip=["category", "order_count", "revenue"]
        ).properties(
            title=f"{query_name} - Orders and Revenue by Category"
        )
    elif "Total_quantity" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="product_id:N",
            y="Total_quantity:Q",
            color="category:N",
            tooltip=["product_id", "category", "Total_quantity", "Revenue", "profit"]
        ).properties(
            title=f"{query_name} - Top Products by Quantity Sold"
        )
    elif "total_quantity" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="region:N",
            y="total_quantity:Q",
            color="region:N",
            tooltip=["region", "total_quantity", "order_count"]
        ).properties(
            title=f"{query_name} - Quantity Sold by Region"
        )
    elif "profit" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="segment:N",
            y="profit:Q",
            color="segment:N",
            tooltip=["segment", "profit"]
        ).properties(
            title=f"{query_name} - Profit by Segment"
        )
    elif "Avg_quantity" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="sub_category:N",
            y="Avg_quantity:Q",
            color="sub_category:N",
            tooltip=["sub_category", "Avg_quantity", "total_order"]
        ).properties(
            title=f"{query_name} - Average Quantity by Sub-Category"
        )
    elif "total_revenue" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="segment:N",
            y="total_revenue:Q",
            color="segment:N",
            tooltip=["segment", "total_revenue"]
        ).properties(
            title=f"{query_name} - Total Revenue by Segment"
        )
    elif "Total_profit" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="region:N",
            y="Total_profit:Q",
            color="region:N",
            tooltip=["region", "Total_profit"]
        ).properties(
            title=f"{query_name} - Total Profit by Region"
        )
    elif "Total_quantity" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="state:N",
            y="Total_quantity:Q",
            color="ship_mode:N",
            tooltip=["state", "Total_quantity", "ship_mode"]
        ).properties(
            title=f"{query_name} - Quantity by State and Shipping Mode"
        )
    elif "profit" in data.columns:
        chart = alt.Chart(data).mark_bar().encode(
            x="order_month:N",
            y="profit:Q",
            color="order_month:N",
            tooltip=["order_month", "profit"]
        ).properties(
            title=f"{query_name} - Profit by Month"
        )
    else:
        return None
    
    return chart

# Queries (same as before)
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
        if data is not None:
            st.write(f"### Results for: {query_selection}")
            st.dataframe(data)
            
            # Generate and display chart
            chart = generate_chart(data, query_selection)
            if chart:
                st.altair_chart(chart, use_container_width=True)
            else:
                st.write("No suitable data found for visualization.")
    except Exception as e:
        st.error(f"Error executing the query: {e}")
