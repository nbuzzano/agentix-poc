"""Example queries for testing"""

# This directory will contain example Teradata queries

TERADATA_QUERY_1 = """
SELECT 
    customer_id,
    customer_name,
    order_id,
    order_date,
    order_amount
FROM customer_orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30' DAY
ORDER BY order_date DESC;
"""

TERADATA_QUERY_2 = """
SELECT 
    product_id,
    product_name,
    COUNT(*) as sales_count,
    SUM(sales_amount) as total_sales,
    AVG(sales_amount) as avg_sale
FROM product_sales
WHERE sale_date >= CAST('2024-01-01' AS DATE)
GROUP BY product_id, product_name
HAVING COUNT(*) > 10
ORDER BY total_sales DESC;
"""

TERADATA_QUERY_WITH_QUALIFY = """
SELECT 
    region,
    salesperson_id,
    total_sales,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_sales DESC) as sales_rank
FROM salesperson_summary
QUALIFY sales_rank <= 5;
"""

TERADATA_QUERY_WITH_JOIN = """
SELECT 
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_amount,
    p.product_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN products p ON o.product_id = p.product_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '90' DAY;
"""

TERADATA_COMPLEX_QUERY = """
WITH ranked_customers AS (
    SELECT 
        customer_id,
        customer_name,
        total_purchases,
        ROW_NUMBER() OVER (ORDER BY total_purchases DESC) as customer_rank
    FROM customer_summary
    WHERE total_purchases > 1000
)
SELECT 
    rc.customer_id,
    rc.customer_name,
    rc.total_purchases,
    rc.customer_rank,
    COUNT(o.order_id) as recent_orders
FROM ranked_customers rc
LEFT JOIN orders o ON rc.customer_id = o.customer_id 
    AND o.order_date >= CURRENT_DATE - INTERVAL '6' MONTH
GROUP BY rc.customer_id, rc.customer_name, rc.total_purchases, rc.customer_rank
QUALIFY customer_rank <= 100;
"""
