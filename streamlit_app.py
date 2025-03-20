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

#Queries
given_queries ={
    "1. Top 10 Highest Revenue Generating Products": """
        SELECT
            category AS product_name,
            SUM(quantity * list_price) AS total_revenue
        FROM orders_csv
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 10;""",
    "2. Top 5 Cities with Highest Profit Margins": """
        SELECT city,
            ROUND(
               CASE
               WHEN SUM(quantity * list_price) = 0 THEN 0  -- Avoid division by zero
               ELSE (SUM(quantity * (list_price - cost_price))::NUMERIC /
                     NULLIF(SUM(quantity * list_price), 0)) * 100
           END, 2) AS profit_margin
        FROM orders_csv WHERE list_price IS NOT NULL AND cost_price IS NOT NULL AND quantity > 0  -- Ensure no missing or invalid data
        GROUP BY city
        ORDER BY profit_margin DESC LIMIT 5;""",
    "3. Calculate the total discount given for each category": """
        SELECT category,
               SUM(COALESCE(list_price, 0) * COALESCE(quantity, 0) * (COALESCE(discount_percent, 0)::NUMERIC / 100)) AS total_discount
        FROM orders_csv
        GROUP BY category
        ORDER BY total_discount DESC;""",
    "4. Find the average sale price per product category":"""
        SELECT category,
               ROUND(SUM(list_price * quantity) / SUM(quantity), 2) AS average_sale_price
        FROM orders_csv
        GROUP BY category
        ORDER BY average_sale_price DESC;""",
    "5. Find the region with the highest average sale price":"""
        SELECT region,
               ROUND(SUM(list_price * quantity) / SUM(quantity), 2) AS average_sale_price
        FROM orders_csv
        GROUP BY region
        ORDER BY average_sale_price DESC;""",
    "6. Find the total profit per category":"""
        SELECT category,
               ROUND(SUM((list_price - cost_price) * quantity) ,2) AS total_profit
        FROM orders_csv
        GROUP BY category
        ORDER BY total_profit DESC;""",
    "7. Identify the top 3 segments with the highest quantity of orders":"""
        SELECT segment,
               SUM(quantity) AS total_quantity
        FROM orders_csv WHERE quantity > 0  -- Ensure no invalid data
        GROUP BY segment
        ORDER BY total_quantity DESC LIMIT 3;""",
    "8. Determine the average discount percentage given per region":"""
        SELECT region,
               ROUND(AVG(discount_percent) ,2) AS average_discount_percentage
        FROM orders_csv
        GROUP BY region
        ORDER BY average_discount_percentage DESC;""",
    "9. Find the product category with the highest total profit":"""
        SELECT category,
               ROUND(SUM((list_price - cost_price) * quantity), 2) AS total_profit
        FROM orders_csv
        GROUP BY category
        ORDER BY total_profit DESC LIMIT 1;""",
    "10.Calculate the total revenue generated per year":"""
        SELECT EXTRACT(YEAR FROM order_date) AS year,
               ROUND(SUM(list_price * quantity), 2) AS total_revenue
        FROM orders_csv
        GROUP BY year
        ORDER BY year;"""
}
own_queries ={
    "1. Select All Orders with Product Details":"""
        SELECT ob.order_id,ob.order_date, ob.region, ob.segment, ob.ship_mode, od.category, od.quantity, od.cost_price, od.list_price
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id;""",
    "2. Find Orders in a Specific Region":"""
        SELECT ob.order_id, ob.order_date, ob.region, ob.city, od.category, od.quantity
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id WHERE ob.region = 'West';""",
    "3. Find All Orders for a Specific Date":"""
        SELECT ob.order_id, ob.order_date, ob.city, ob.state, od.category, od.quantity
        FROM orders_basic ob JOIN orders_details od ON ob.order_id = od.order_id WHERE ob.order_date = '2022-06-20';""",
    "4. Find Total Discount per Order":"""
        SELECT ob.order_id,
              SUM(od.quantity * od.list_price * (od.discount_percent / 100)) AS total_discount
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id
        GROUP BY ob.order_id ORDER BY total_discount DESC;""",
    "5. Get Orders for a Specific Customer Segment":"""
        SELECT ob.order_id, ob.order_date, ob.segment, od.category, od.quantity
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id WHERE ob.segment = 'Corporate';""",
    "6. Calculate the Average List Price of Products":"""
        SELECT ob.order_id, AVG(od.list_price) AS avg_list_price
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id
        GROUP BY ob.order_id
        ORDER BY avg_list_price DESC;""",
    "7. Find Orders with the Highest Quantity Ordered":"""
        SELECT ob.order_id, ob.order_date,
               SUM(od.quantity) AS total_quantity
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id
        GROUP BY ob.order_id
        ORDER BY total_quantity DESC LIMIT 10;""",
    "8. Find Total Revenue Per Order":"""
        SELECT ob.order_id,
              SUM(od.quantity * od.list_price) AS total_revenue
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id
        GROUP BY ob.order_id
        ORDER BY total_revenue DESC;""",
    "9. Find the Total Profit for Each Order":"""
        SELECT ob.order_id,
              SUM((od.list_price - od.cost_price) * od.quantity) AS total_profit
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id
        GROUP BY ob.order_id
        ORDER BY total_profit DESC;""",
    "10.Get All Orders with Their Total Discount Applied":"""
        SELECT ob.order_id,
               SUM(od.quantity * od.list_price * (od.discount_percent / 100)) AS total_discount
        FROM orders_basic ob
        JOIN orders_details od ON ob.order_id = od.order_id
        GROUP BY ob.order_id
        ORDER BY total_discount DESC;"""
}

# Streamlit UI
st.title("Retail Order Data Analysts Project")
st.sidebar.title("Options")

query_type = st.sidebar.radio("Query Type:", ["Given Queries", "Own Queries"])
query_selection = st.selectbox(
    "Select a Query:",
    list(given_queries.keys() if query_type == "Given Queries" else own_queries.keys()),
)

data = pd.read_csv("data.csv")
if conn:
    if st.button("Run Query"):
        query = given_queries[query_selection] if query_type == "Given Queries" else own_queries[query_selection]
        try:
            # Execute query and fetch results
            data = pd.read_sql_query(query, conn)
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

        except Exception as e:
               st.error("Error executing the query.")
               st.error(f"Error: {e}")
else:
    st.warning("Database connection is not available.")
