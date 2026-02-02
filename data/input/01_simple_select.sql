-- Ejemplo 1: Query simple SELECT
SELECT 
    customer_id,
    customer_name,
    total_purchases
FROM customers
WHERE status = 'ACTIVE'
ORDER BY total_purchases DESC;