import psycopg

try:
    conn = psycopg.connect('postgresql://postgres:root@localhost:5432/postgres', autocommit=True)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'airwise_ai'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE airwise_ai;')
            print('Database airwise_ai created successfully!')
        else:
            print('Database airwise_ai already exists!')
    conn.close()
except Exception as e:
    print('Error:', e)
