from random import randrange

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

from wtforms import ValidationError

from forms import CreateAccount, MakeTransaction, Deposit

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = '4ee15591724bb71d32bab5816a2ff3fd'


def get_conn():
	connection = sqlite3.connect('database.db')
	connection.row_factory = sqlite3.Row
	return connection


def fetch_account(cursor, _id: int):
	cursor.execute("select * from account where id = ?;", [_id])
	return cursor.fetchone()


@app.route("/")
def index():
	conn = get_conn()
	cursor = conn.cursor()
	query = '''
				select * from account;
			'''
	cursor.execute(query)
	res = [dict(row) for row in cursor.fetchall()]
	max_balances = {'KZT': 0, 'USD': 0, 'EUR': 0}
	for record in res:
		if float(record['balance']) > max_balances[record['currency']]:
			max_balances[record['currency']] = float(record['balance'])
	return render_template('index.html', table=res, title='Все счета', tohighlight=max_balances)


@app.route("/create", methods=['GET', 'POST'])
def create_account():
	create = CreateAccount()
	if request.method == 'POST':
		conn = get_conn()
		cursor = conn.cursor()
		try:
			_id = randrange(10000)
			currency = request.form['currency']
			cursor.execute('''
							insert into account (id, currency, balance) VALUES (?, ?, ?)
			''', (int(_id), currency, 0))
			conn.commit()
			flash('Счет создан успешно')
		except:
			flash('Ошибка при создании счета')
			conn.rollback()
		finally:
			conn.close()
			return redirect(url_for('index'))
	return render_template('create.html', title='Create Account', form=create)


@app.route("/<accountid>")
def see_transactions(accountid):
	conn = get_conn()
	cur = conn.cursor()
	try:
		q = '''
				select * from "transaction" where from_account = ? or to_account = ?;
			'''
		cur.execute(q, [float(accountid), float(accountid)])
		res = [dict(row) for row in cur.fetchall()]
	except:
		flash('Ошибка при получении данных')
		return redirect(url_for('index'))
	return render_template('transactions.html', table=res, title='Транзакции по счету #' + accountid,
							acc_id=accountid)


@app.route("/<accountid>/send", methods=['GET', 'POST'])
def make_transaction(accountid):
	trans = MakeTransaction()
	if request.method == 'POST':
		conn = get_conn()
		cursor = conn.cursor()
		try:
			receiverid = int(request.form['to_account'])
			amount = float(request.form['amount'])

			sender = fetch_account(cursor, accountid)
			receiver = fetch_account(cursor, receiverid)

			if sender['currency'] == receiver['currency'] and float(sender['balance']) >= amount:
				cursor.execute('update account set balance = ? where id = ?;',
				               [float(sender['balance']) - amount, int(sender['id'])])
				cursor.execute("update account set balance = ? where id = ?;",
				               [float(receiver['balance']) + amount - 100,
				                int(receiver['id'])])
				cursor.execute('''insert into "transaction"
						(id, from_account, to_account, balance_sent, balance_received, currency, status) 
						values (?,?,?,?,?,?,?);''',
				               [randrange(10000), int(sender['id']), int(receiver['id']), amount, amount - 100,
				                sender['currency'], "Completed"])
				conn.commit()
			else:
				if sender['currency'] != receiver['currency']:
					flash('Валюта счетов должна совпадать')
				if float(sender['balance']) < amount:
					flash('Недостаточно средств')
		except ValidationError:
			flash('Неправильный ввод')
		except:
			flash('Перевод не удался')
		finally:
			conn.close()
		return redirect(url_for('index'))
	return render_template('maketransaction.html', title='Make a transaction', form=trans)


@app.route("/<accountid>/deposit", methods=['GET', 'POST'])
def deposit(accountid):
	depo = Deposit()
	conn = get_conn()
	cursor = conn.cursor()
	if request.method == 'POST':
		try:
			amount = float(request.form['amount'])
			account = fetch_account(cursor, accountid)
			q = '''
					update account set balance = ? where id = ?;
				'''
			cursor.execute(q, [account['balance'] + amount, account['id']])
			conn.commit()
			flash('Пополнение успешно')
		except ValidationError:
			flash('Неправильный ввод')
		except:
			flash('Пополнение не удалось')
			conn.rollback()
		finally:
			conn.close()
			return redirect(url_for('index'))
	return render_template('deposit.html', title='Deposit to balance', form=depo)


if __name__ == '__main__':
	app.run(debug=True)
