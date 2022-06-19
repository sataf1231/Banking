from enum import unique
import json
from re import U
from tokenize import String
import requests
from flask import Flask, Request, Response, jsonify, request
import base64
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime, timedelta,date
from sqlalchemy import func, between


app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:0257@localhost:5432/sql_banking'

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name_user = db.Column(db.String(20), nullable=False)
	username = db.Column(db.String(20), nullable=False, unique=True)
	password = db.Column(db.String(20), nullable=False)
	phone = db.Column(db.Numeric(15,2), nullable=False)
	address = db.Column(db.String, nullable=False)
	email = db.Column(db.String(50), nullable=False, unique=True)
	is_admin = db.Column(db.Boolean, nullable=False)
	usera = db.relationship('Account', backref='usera')

	def __repr__(self):
		return f'User: <{self.name_user}>'

class Branch(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name_branch = db.Column(db.String(20), nullable=False)
	city = db.Column(db.String(20), nullable=False)
	brancha = db.relationship('Account', backref='brancha')

	def __repr__(self):
		return f'Branch: <{self.name_branch}>'

class Account(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	no_account = db.Column(db.Numeric(15), nullable=False, unique=True)
	name_account = db.Column(db.String(50), nullable=False)
	balance = db.Column(db.Integer, nullable=False)
	status = db.Column(db.String(20), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)

	def __repr__(self):
		return f'Account: <{self.name_account}>'

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	date_transaction = db.Column(db.Date)
	amount = db.Column(db.Integer, nullable=False)
	desc = db.Column(db.String, nullable=False)
	from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
	to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), default=0)

	def __repr__(self):
		return f'Transaction: <{self.amount}>'

# db.create_all()
# db.session.commit()

#---------------Auth-------------------
@app.route('/auth')
def auth(a):
	c = base64.b64decode(a[6:])
	e = c.decode("ascii")
	lis = e.split(':')
	username = lis[0]
	passw = lis [1]
	user = User.query.filter_by(username=username).filter_by(password=passw).first()
	if not user:
		return 'Please check login detail'
	elif user:
		return [username, passw]

#---------------------User----------------------#
#Get
@app.route('/user/')
def get_user():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user.is_admin == True:
		return jsonify([
				{
					'id': i.public_id, 'name': i.name_user, 'username':i.username, 'password':i.password,'phone':i.phone,
					'address':i.address,'email':i.email
					} for i in User.query.all()
			]),200
	elif user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Get ID
@app.route('/user/<id>/')
def get_user_id(id):
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user:
		u = User.query.filter_by(public_id=id).first_or_404()
		return jsonify([
				{
				 'name': u.name_user, 'username':u.username, 'phone':u.phone,
					'address':u.address,'email':u.email
					}
			]),201

#Insert
@app.route('/user/', methods=['POST'])
def create_user():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		data = request.get_json()
		if not 'name_user' in data:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name not given'
			}), 400
		if len(data['email']) < 5:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Email must be contain minimum of 5 letters'
			}), 400
		u = User(
				name_user=data['name_user'],
				username=data['username'],
				password=data['password'],
				phone=data['phone'],
				address=data['address'],
				email=data['email'],
				is_admin=data.get('is_admin', False),
				public_id=str(uuid.uuid4())
			)
		db.session.add(u)
		db.session.commit()
		return {
			'name user': u.name_user,
			'username':u.username,
			'password':u.password,
			'phone':u.phone,
			'address':u.address,
			'email':u.email,
		}, 201
	elif user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Update Data
@app.route('/user/', methods=['PUT'])
def update_user():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	allow1 = auth(decode)[1]
	user = User.query.filter_by(username=allow).filter_by(password=allow1).first_or_404()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user:
		if 'name_user' not in data:
			return {
				'error': 'Bad Request',
				'message': 'Name field needs to be present'
			}, 400
		user.name_user=data['name_user']
		user.password=data['password']
		user.phone=data['phone']
		user.address=data['address']
		user.email=data['email']
		db.session.commit()
		return jsonify({
			'name': user.name_user, 'username':user.username,'password':user.password,'address':user.address,
			'phone':user.phone,'email':user.email
			}),200

#---------------------Branch-----------------#
#Get
@app.route('/branch/')
def get_branch():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		return jsonify([
				{
					'id': i.public_id, 'name_branch': i.name_branch, 'city':i.city
					} for i in Branch.query.all()
			])
	elif user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Insert
@app.route('/branch/', methods=['POST'])
def create_branch():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		if not 'name_branch' in data:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name not given'
			}), 400
		b = Branch( 
				name_branch=data['name_branch'],
				city=data['city'],
				public_id=str(uuid.uuid4())
			)
		db.session.add(b)
		db.session.commit()
		return {
			'name branch': b.name_branch,
			'city': b.city
		}, 201
	elif user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Update Data
@app.route('/branch/<id>/', methods=['PUT'])
def update_branch(id):
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user.is_admin == True:
		if 'name_branch' not in data:
			return {
				'error': 'Bad Request',
				'message': 'Name field needs to be present'
			}, 400
		branch = Branch.query.filter_by(public_id=id).first()
		branch.name_branch=data['name_branch']
		branch.city=data['city']
		db.session.commit()
		return jsonify({
			'name': branch.name_branch, 'city':branch.city,
			}),200
	elif user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401


#--------------------Account-------------------------#
#Get
@app.route('/account/')
def get_account():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		return jsonify([
				{
					'id': i.public_id, 
					'name account': i.name_account, 
					'balance':i.balance,
					'status':i.status,
					'no account':i.no_account,
					'user ':i.usera.name_user,
					'branch ':i.brancha.name_branch,
					} for i in Account.query.all()
			])
	elif user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Get ID
@app.route('/account-id/')
def get_account_id():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	allow1 = auth(decode)[1]
	user = User.query.filter_by(username=allow).filter_by(password=allow1).first_or_404()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user:
		acc = Account.query.filter_by(user_id=user.id).all()
		lis = []
		for x in acc:
			lis.append(
					{
						'name account': x.name_account, 
						'balance':x.balance,
						'status':x.status,
						'no account':x.no_account,
						'user ':x.usera.name_user,
						'branch ':x.brancha.name_branch,
						}
				)	
		return jsonify(lis)

#Insert
@app.route('/account/', methods=['POST'])
def create_account():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		user = User.query.filter_by(username=data['username']).first()
		if not user:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Username not given'
			}), 400
		branch = Branch.query.filter_by(name_branch=data['name_branch']).first()
		if not branch:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Branch not given'
			}), 400
		a = Account( 
				name_account=data['name_account'],
				balance=data.get('balance',50000),
				status=data.get('status','Active'),
				no_account=data['no_account'],
				user_id=user.id,
				branch_id=branch.id,
				public_id=str(uuid.uuid4())
			)
		db.session.add(a)
		db.session.commit()
		return {
			'Account Name': a.name_account,'Balance': a.balance,'Status': a.status,'User Id': a.user_id,'Branch Id': a.branch_id
		}, 201
	elif user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Update Data
@app.route('/account/<id>/', methods=['PUT'])
def update_account(id):
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user.is_admin == True:
		if 'status' not in data:
			return {
				'error': 'Bad Request',
				'message': 'Name field needs to be present'
			}, 400
		acc = Account.query.filter_by(public_id=id).first()
		acc.status = data['status']
		db.session.commit()
		return jsonify({
			'no account': acc.no_account, 'name account':acc.name_account, 'status':acc.status
			}),200
	elif user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401
#Delete
@app.route('/account/<id>/', methods=['DELETE'] )
def delete_account(id):
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin == True:
		acc = Account.query.filter_by(public_id=id).first_or_404()
		db.session.delete(acc)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		}

#-------------Transaction------------------#
#Save
@app.route('/save/', methods=['POST'])
def create_save():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		return {
			'message':'Youre unauthorize to do that.'
		},401
	if user.is_admin == False:
		if (data['amount']) < 10000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Minimum amount is 10000'
			}), 400
		acc = Account.query.filter_by(no_account=data['no_account']).first()
		t = Transaction( 
				date_transaction=data['date_transaction'],
				amount=data['amount'],
				desc=data.get('desc','Save'),
				from_account_id=acc.id,
				to_account_id=acc.id,
				public_id=str(uuid.uuid4())
			)
		acc.balance += t.amount	
		db.session.add(t)
		db.session.commit()
		return {
			"message":"Success"
			# 'name account': t.name_account,
			# 'balance': t.balance,
			# 'status': t.status,
			# 'user id': t.user_id,
			# 'branch id': t.branch_id
		}, 201
		
#Witdraw
@app.route('/withdraw/', methods=['POST'])
def create_withdraw():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	allow1 = auth(decode)[1]
	user = User.query.filter_by(username=allow).filter_by(password=allow1).first_or_404()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		return {
			'message':'Youre unauthorize to do that.'
		},401
	if user.is_admin == False:
		acc = Account.query.filter_by(no_account=data['no_account']).first()
		acc_ = Account.query.filter_by(no_account=acc.no_account).filter_by(user_id=user.id).first()
		if not acc_:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not your account'
			}), 400
		if acc.balance <= 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400
		if (data['amount']) < 10000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Minimum amount is 10000'
			}), 400
		if (data['amount']) > acc.balance:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400
		t = Transaction( 
				date_transaction=data['date_transaction'],
				amount=data['amount'],
				desc=data.get('desc','Withdraw'),
				from_account_id=acc.id,
				to_account_id=acc.id,
				public_id=str(uuid.uuid4())
			)
		acc.balance -= t.amount
		if acc.balance < 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400	
		db.session.add(t)
		db.session.commit()
		return {
			"message":"Success"
			# 'name account': t.name_account,
			# 'balance': t.balance,
			# 'status': t.status,
			# 'user id': t.user_id,
			# 'branch id': t.branch_id
		}, 201

#Transfer
@app.route('/transfer/', methods=['POST'])
def create_transfer():
	data = request.get_json()
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).filter_by(password=allow1).first_or_404()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		return {
			'message':'Youre unauthorize to do that.'
		},401
	if (data['amount']) < 10000:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Minimum amount is 10000'
		}), 400
	if user.is_admin == False:
		acc = Account.query.filter_by(no_account=data["no_account"][0]).first()
		acc1 = Account.query.filter_by(no_account=acc.no_account).filter_by(user_id=user.id).first()
		if not acc1:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not your account'
			}), 400
		acc2 = Account.query.filter_by(no_account=data["no_account"][1]).first()
		if acc.balance <= 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400
		t = Transaction( 
				date_transaction=data['date_transaction'],
				amount=data['amount'],
				desc=data.get('desc',"Transfer"),
				from_account_id=acc1.id,
				to_account_id=acc2.id,
				public_id=str(uuid.uuid4())
			)
		acc.balance -= t.amount
		if acc.balance < 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400	
		acc1.balance += t.amount		
		db.session.add(t)
		db.session.commit()
		return {
			"message":"Success"
		}, 201

#History
@app.route('/history/<id>/') #Find berdasarkan nomor account
def get_history(id):
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	allow1 = auth(decode)[1]
	user = User.query.filter_by(username=allow).filter_by(password=allow1).first_or_404()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif user:
		lst = []
		# acc = Account.query.filter_by(no_account=id).first()
		acc = Account.query.filter_by(no_account=id).filter_by(user_id=user.id).first()
		if not acc:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not your account'
			}), 400
		i = Transaction.query.filter_by(from_account_id=acc.id).order_by(Transaction.date_transaction.desc()).all()
		for x in i:
			lst.append({'Transaction Date': x.date_transaction, 'Amount':x.amount, 'Desc':x.desc,'From Account':x.from_account_id,
					'To Account':x.to_account_id})
		return jsonify(lst),201

#DB Execute Branch Report 1
@app.route('/report1/', methods=['POST'])
def get_report1():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		data = request.get_json()
		branch = Branch.query.filter_by(name_branch=data['name_branch']).first()
		# result = db.engine.execute('''SELECT SUM(amount), "%s" FROM transaction WHERE (date_transaction BETWEEN '%s' AND '%s')GROUP BY "%s" ORDER BY SUM DESC'''%("desc",data['date'], data['date1'], "desc".strip()))
		result = db.engine.execute('''SELECT SUM(t.amount), t."%s" FROM transaction t INNER JOIN account a ON a.id = t.from_account_id INNER JOIN branch ON branch.id = a.branch_id WHERE (date_transaction BETWEEN '%s' AND '%s') AND a.branch_id = '%s' GROUP BY "%s" ORDER BY SUM DESC'''%("desc",data['date'], data['date1'],branch.id, "desc".strip()))
		x = []
		for y in result:
			x.append({'Total Amount':y[0], 'Event':y[1]})
		return jsonify(x)
	elif user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#DB Execute Branch Report 2
@app.route('/report2/', methods=['POST'])
def get_report2():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
					'message' : 'Check your login details.'
				}, 401
	if user.is_admin == True:
		data = request.get_json()
		branch = Branch.query.filter_by(name_branch=data['name_branch']).first()
		result = db.engine.execute('''SELECT COUNT(u.id),COUNT(a.no_account),SUM(a.balance) FROM account a INNER JOIN branch b ON b.id = a.branch_id INNER JOIN "%s" u ON a.user_id=u.id WHERE a.branch_id = '%s' '''%("user", branch.id))
		x = []
		for y in result:
			x.append({'Total User':y[0], 'Total Account':y[1],'Total Balance':y[2]})
		return jsonify(x)
	elif user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Dormant Report
@app.route('/report-dormant/')
def get_dormant_report():
	decode = request.headers.get('Authorization')
	allow = auth(decode)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if user.is_admin == True:
		test = get_time()
		lsta = []
		lstb = []
		lstc = []
		lstd = []
		t = Transaction.query.filter(Transaction.date_transaction.between(test[0],test[1])).all()
		acc_ = Account.query.all()
		for y in acc_:
			lsta.append(y.id)
		for x in t:
			acc = Account.query.filter_by(id=x.from_account_id).first()
			lstb.append(acc.id)
		for j in range(len(lsta)):
			if lsta[j] not in lstb:
				lstc.append(lsta[j])
		for q in lstc:
			t = Account.query.filter_by(id=q).first()
			trans = Transaction.query.filter_by(from_account_id=q).order_by(Transaction.id.desc()).first()
			time = datetime.today().strftime('%m')
			time2 = int(time)-int(trans.date_transaction.strftime('%m'))
			time3 = int(datetime.today().strftime('%d'))
			time4 = int(trans.date_transaction.strftime('%d'))
			time5 = 0
			time6 = 0
			if time3 < time4:
				time5 = 30 - (time4-time3)
				time6 = time2 - 1
			elif time4 < time3:
				time5 = time3 - time4
				time6 = time2
			lstd.append({'Account Number': t.no_account, "Dormant Duration(Days)": (time6 * 30)+time5, "Account Name":t.name_account})
		return jsonify(lstd),201
	elif user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

# @app.route('/')
def get_time():
	lst = []
	a = datetime.today().strftime('%Y-%m-%d')
	b = datetime.today() + timedelta(days=-90)
	# return a.strftime('%Y-%m-%d')
	lst.append(b.strftime('%Y-%m-%d'))
	lst.append(a)
	return lst

