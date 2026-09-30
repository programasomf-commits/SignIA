from backend.database import get_connection


connection = get_connection()

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