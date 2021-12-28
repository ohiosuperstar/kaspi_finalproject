from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class CreateAccount(FlaskForm):
	currency = RadioField('Валюта:', validators=[DataRequired()], choices=[('KZT', 'KZT'), ('USD', 'USD'), ('EUR', 'EUR')])
	submit = SubmitField('Создать счет')


class MakeTransaction(FlaskForm):
	to_account = IntegerField('Идентификатор получателя: ', validators=[DataRequired()])
	amount = FloatField('Сумма перевода: ', validators=[DataRequired(), NumberRange(min=101)])
	submit = SubmitField('Отправить')


class Deposit(FlaskForm):
	amount = FloatField('Сумма: ', validators=[DataRequired()])
	submit = SubmitField('Пополнить')




