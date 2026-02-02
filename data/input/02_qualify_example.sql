-- Ejemplo 2: Query con QUALIFY (Teradata-specific)
SELECT 
    region,
    salesperson_id,
    total_sales,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_sales DESC) as rank
FROM salesperson_summary
WHERE fiscal_year = 2024
QUALIFY rank <= 5;