import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()


query = '''
			select * from account;
		'''
cursor.execute(query)
print(cursor.fetchall())