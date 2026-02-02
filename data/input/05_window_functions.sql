-- Ejemplo 5: Query con Window Functions
SELECT 
    employee_id,
    employee_name,
    salary,
    department,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
    RANK() OVER (ORDER BY salary DESC) as overall_rank,
    LEAD(salary) OVER (PARTITION BY department ORDER BY salary DESC) as next_salary,
    LAG(salary) OVER (PARTITION BY department ORDER BY salary DESC) as prev_salary,
    SUM(salary) OVER (PARTITION BY department) as dept_total_salary
FROM employees
WHERE hire_date >= '2020-01-01'
ORDER BY department, salary DESC;