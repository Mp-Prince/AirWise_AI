import psycopg

# Create airwise_ai database
conn = psycopg.connect('postgresql://postgres:root@localhost:5432/postgres', autocommit=True)
with conn.cursor() as cur:
    cur.execute('DROP DATABASE IF EXISTS airwise_ai;')
    cur.execute('CREATE DATABASE airwise_ai;')
    print('Database airwise_ai created successfully')
conn.close()