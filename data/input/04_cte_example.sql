-- Ejemplo 4: Query con CTE (Common Table Expression)
WITH recent_orders AS (
    SELECT 
        customer_id,
        order_id,
        order_date,
        order_amount
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '90' DAY
),
customer_summary AS (
    SELECT 
        customer_id,
        COUNT(*) as recent_order_count,
        AVG(order_amount) as avg_order_value,
        MAX(order_date) as last_order_date
    FROM recent_orders
    GROUP BY customer_id
)
SELECT 
    c.customer_id,
    c.customer_name,
    cs.recent_order_count,
    cs.avg_order_value,
    cs.last_order_date
FROM customers c
INNER JOIN customer_summary cs ON c.customer_id = cs.customer_id
WHERE cs.recent_order_count >= 2
ORDER BY cs.avg_order_value DESC;