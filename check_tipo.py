import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Ver constraint del tipo
cur.execute("""
    SELECT pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conname LIKE '%tipo%' 
    AND conrelid = 'codigos_temporales'::regclass
""")

results = cur.fetchall()
print("Constraints en codigos_temporales:")
for r in results:
    print(r[0])

conn.close()
