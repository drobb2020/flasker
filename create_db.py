import mysql.connector


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Excess10n'
)

my_cursor = mydb.cursor()

# my_cursor.execute('CREATE DATABASE flasker')

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
