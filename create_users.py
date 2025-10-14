#!/usr/bin/env python3
import bcrypt
import psycopg2

# Generate hash
password = b'Demo2025!'
hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))
hashed_str = hashed.decode('utf-8')

print(f"Generated hash: {hashed_str}")
print(f"Verifying: {bcrypt.checkpw(password, hashed)}")

# Connect to database
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='financia_db',
    user='financia',
    password='financia2030'
)

cur = conn.cursor()

# Delete existing users
cur.execute("DELETE FROM users")

# Insert new users
users = [
    ('admin@demo.documental.com', 'Administrador Demo', 'ADMIN', 'IT'),
    ('usuario@demo.documental.com', 'Juan Usuario', 'USER', 'Operaciones'),
    ('revisor@demo.documental.com', 'María Revisor', 'REVIEWER', 'Calidad'),
]

for email, full_name, role, department in users:
    cur.execute("""
        INSERT INTO users (id, email, full_name, hashed_password, role, department, is_active, created_at)
        VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, true, now())
    """, (email, full_name, hashed_str, role, department))
    print(f"✅ Created user: {email}")

conn.commit()
cur.close()
conn.close()

print("\n✅ All users created successfully!")
