import random
import sqlite3
from random import randrange


def get_conn():
	connection = sqlite3.connect('database.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	return connection


conn = get_conn()
c = conn.cursor()
query = '''
			select * from account;
		'''
c.execute(query)
res = [dict(row) for row in c.fetchall()]

ids = {}
for d in res:
	ids[d['id']] = d['currency']
print(ids)

for i in range(27):
	id1, cur1 = random.choice(list(ids.items()))
	id2, cur2 = random.choice(list(ids.items()))
	while id1 == id2 or cur1 != cur2:
		id1, cur1 = random.choice(list(ids.items()))
		id2, cur2 = random.choice(list(ids.items()))
	b = randrange(101, 100000)
	c.execute('''
				insert into "transaction" (id, from_account, to_account, balance_sent, balance_received, currency, status)
				VALUES (?, ?, ?, ?, ?, ?, ?);
			''', (randrange(10000), id1, id2, b, b - 100, cur1, random.choice(['Completed', 'Pending'])))
	conn.commit()
