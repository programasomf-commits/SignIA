import psycopg


connection = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="signia_db",
    user="postgres",
    password="qwerty.12345"
)


cursor = connection.cursor()

cursor.execute(
    "SELECT id, component, status FROM integration_test;"
)

rows = cursor.fetchall()

print("Registros encontrados:")

for row in rows:
    print(row)


cursor.close()
connection.close()