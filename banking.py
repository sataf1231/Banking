from audioop import add
import base64,uuid,json,requests,jwt, datetime
from lib2to3.pgen2 import token
from functools import wraps
from enum import unique
from re import U
from tokenize import String
from flask import Flask, Request, Response, jsonify, request,make_response
from flask_cors import CORS,cross_origin
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta,date,datetime
from sqlalchemy import func, between

app = Flask(__name__)
db = SQLAlchemy(app)
CORS(app,supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:0257@localhost:5432/db_banking'
app.config['SECRET_KEY']='internet banking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name_user = db.Column(db.String(50), nullable=False)
	username = db.Column(db.String(20), nullable=False, unique=True)
	password = db.Column(db.String(20), nullable=False)
	phone = db.Column(db.Numeric(16), nullable=False)
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
	name_account = db.Column(db.String(50), nullable=False)
	balance = db.Column(db.Integer, nullable=False)
	status = db.Column(db.String(20), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'), nullable=False)
	# accounttrans = db.relationship('Transaction', backref='accounttrans')

	def __repr__(self):
		return f'Account: <{self.name_account}>'

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	date_transaction = db.Column(db.Date)
	amount = db.Column(db.Integer, nullable=False)
	desc = db.Column(db.String, nullable=False)
	from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'),nullable=False)
	to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

	def __repr__(self):
		return f'Transaction: <{self.amount}>'

# db.create_all()
# db.session.commit()

#--------------Token------------------
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
				token = request.headers['x-access-token']
		if not token:
				return jsonify({'message' : 'Token is missing !!'}), 401
		try:
				data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
				current_user = User.query.filter_by(username=data['username']).first()
		except:
				return jsonify({
						'message' : 'Token is invalid !!'
				}), 401
		return  f(current_user,*args, **kwargs)
	return decorated

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

#--------------------Login-------------------
@app.route('/login/', methods=['POST']) 
@cross_origin(supports_credentials= True)
def login_user():
	decode_var = request.headers.get('Authorization')
	allow = auth(decode_var)[0]
	allowpass = auth(decode_var)[1] 
	user = User.query.filter_by(username=allow).filter_by(password=allowpass).first()  
	if not user:
		return make_response('Please check your login detail',401)

	elif user:
		token = jwt.encode({'public_id' : user.public_id,'is_admin' : user.is_admin, 'name_user':user.name_user,'username': user.username,'exp' : datetime.now() + timedelta(hours=1)}, app.config['SECRET_KEY'])
		return make_response(jsonify({'token':token}),201)

	else:
		return make_response('could not verify',  401, {'Authentication': '"login required"'})

#---------------------User----------------------#
#Get
@app.route('/user/')
def get_user():
	decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 			'message' : 'Check your login details.'
	# 		}, 401
	# elif user.is_admin == True:
	return jsonify([
			{
				'id': i.public_id, 'name_user': i.name_user, 'username':i.username, 'password':i.password,'phone':i.phone,
				'address':i.address,'email':i.email
				} for i in User.query.all()
		]),200
	# elif user.is_admin is False:
	# 	return {
	# 		'message':'Youre unauthorize to do that.'
	# 	},401

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
		u = User.query.filter_by(public_id=id).first()
		return jsonify([
				{
				 'name_user': u.name_user, 'username':u.username, 'phone':u.phone,
					'address':u.address,'email':u.email
					}
			]),201

#Insert
@app.route('/user/', methods=['POST'])
@token_required
def create_user(current_user):
	data = request.get_json()
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
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
			'name_user': u.name_user,
			'username':u.username,
			'password':u.password,
			'phone':u.phone,
			'address':u.address,
			'email':u.email,
	}, 201
	elif current_user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Update Data Password
@app.route('/user_password/', methods=['PUT'])
@token_required
def update_user_password(current_user):
	data = request.get_json()
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(username=allow).filter_by(password=allow1).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif current_user:
		if 'password' not in data:
			return {
				'error': 'Bad Request',
				'message': 'Name field needs to be present'
			}, 400
		current_user.password=data['password']
		db.session.commit()
		return jsonify({
			'message': "Update success"
			}),200

#Update Data
@app.route('/user_update/<id>/', methods=['PUT'])
@token_required
def update_user_data(current_user,id):
	data = request.get_json()
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(username=allow).filter_by(password=allow1).first()
	user = User.query.filter_by(public_id=id).first_or_404()
	if current_user.is_admin == False:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif current_user.is_admin == True:
		if 'name_user' not in data:
			return {
				'error': 'Bad Request',
				'message': 'Name field needs to be present'
			}, 400
		user.name_user=data['name_user']
		user.phone=data['phone']
		user.address=data['address']
		user.email=data['email']
		db.session.commit()
		return jsonify({
			'message': "Update success"
			}),200


#---------------------Branch-----------------#
#Get
@app.route('/branch/')
def get_branch():
	decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 			'message' : 'Check your login details.'
	# 		}, 401
	# if user.is_admin == True:
	return jsonify([
			{
				'id': i.public_id, 'name_branch': i.name_branch, 'city':i.city
				} for i in Branch.query.all()
		]),201
	# elif user.is_admin == False:
	# 	return {
	# 		'message':'Youre unauthorize to do that.'
	# 	},401

#Insert
@app.route('/create_branch/', methods=['POST'])
@token_required
def create_branch(current_user):
	data = request.get_json()
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
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
			'name_branch': b.name_branch,
			'city': b.city
		}, 201
	elif current_user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Update Data
@app.route('/branch/<id>/', methods=['PUT'])
@token_required
def update_branch(current_user,id):
	data = request.get_json()
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif current_user.is_admin == True:
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
			'name_branch': branch.name_branch, 'city':branch.city,
			}),200
	elif current_user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#--------------------Account-------------------------#
#Get
@app.route('/account/')
def get_account():
	decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 			'message' : 'Check your login details.'
	# 		}, 401
	# if user.is_admin == True:
	return jsonify([
			{
				'id': i.id, 
				'name_account': i.name_account, 
				'balance':i.balance,
				'status':i.status,
				'user_name':i.usera.name_user,
				'branch_name':i.brancha.name_branch,
				} for i in Account.query.all()
		])
	# elif user.is_admin == False:
	# 	return {
	# 		'message':'Youre unauthorize to do that.'
	# 	},401

#Get ID
@app.route('/account_id/')
@token_required
def get_account_id(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(public_id=public_id).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif current_user:
		acc = Account.query.filter_by(user_id=current_user.id).order_by(Account.id.desc()).all()
		lis = []
		for x in acc:
			lis.append(
					{
						'id': x.id,
						'name_account': x.name_account, 
						'balance':x.balance,
						'status':x.status,
						'user_name':x.usera.name_user,
						'branch_name':x.brancha.name_branch,
						}
				)	
		return jsonify(lis)

#Insert
@app.route('/account/', methods=['POST'])
@token_required
def create_account(current_user):
	data = request.get_json()
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
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
				user_id=user.id,
				branch_id=branch.id
			)
		db.session.add(a)
		db.session.commit()
		return {
			'id': a.id,'name_account': a.name_account,'balance': a.balance,'status': a.status,'user_id': a.user_id,'branch_id': a.branch_id
		}, 201
	elif current_user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Update Data
@app.route('/account/<id>/', methods=['PUT'])
@token_required
def update_account(current_user,id):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	acc = Account.query.filter_by(id=id).first_or_404()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	elif current_user.is_admin == True:
		if acc.status == 'Active':
			acc.status = 'Inactive'
			db.session.commit()
		elif acc.status == 'Inactive':
			acc.status = 'Active'
			db.session.commit()
		return jsonify({
			'id': acc.id, 'name_account':acc.name_account, 'status':acc.status
			}),200
	elif current_user.is_admin is False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#-------------Transaction------------------#
#Save
@app.route('/save/', methods=['POST'])
@token_required
def create_save(current_user):
	data = request.get_json()
	decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(username=allow).filter_by(password=allow1).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
		return {
			'message':'Youre unauthorize to do that.'
		},401
	if current_user.is_admin == False:
		if (data['amount']) < 10000:
			return make_response(jsonify({
				'error': 'Bad Request',
				'message': 'Minimum amount is 10000'
			}), 400)
		acc = Account.query.filter_by(id=data['id']).filter_by(user_id=current_user.id).first()
		if not acc:
			return make_response(jsonify({
				'error': 'Bad Request',
				'message': 'Not your account'
			}), 400	)
		if acc.status == 'Inactive':
			return make_response(jsonify({
				'error': 'Bad Request',
				'message': 'Your account is inactive'
			}), 400	)
		t = Transaction( 
				date_transaction=datetime.today().strftime('%Y-%m-%d'),
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
		}, 201
		
#Witdraw
@app.route('/withdraw/', methods=['POST'])
@token_required
def create_withdraw(current_user):
	data = request.get_json()
	decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(username=allow).filter_by(password=allow1).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
		return {
			'message':'Youre unauthorize to do that.'
		},401
	if current_user.is_admin == False:
		acc = Account.query.filter_by(id=data['id']).filter_by(user_id=current_user.id).first()
		if not acc:
			return jsonify({
				'message': 'Not your account'
			}), 401
		if acc.status == 'Inactive':
			return jsonify({
				'error': 'Bad Request',
				'message': 'Your account is inactive'
			}), 400	
		if acc.balance <= 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400
		if (data['amount']) < 10000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Minimum withdraw is 10000'
			}), 400
		if (data['amount']) > acc.balance:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400
		t = Transaction( 
				date_transaction=datetime.today().strftime('%Y-%m-%d'),
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
		}, 201

#Transfer
@app.route('/transfer/', methods=['POST'])
@token_required
def create_transfer(current_user):
	data = request.get_json()
	decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(username=allow).filter_by(password=allow1).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
		return {
			'message':'Youre unauthorize to do that.'
		},401
	if (data['amount']) < 10000:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Minimum amount is 10000'
		}), 400
	if current_user.is_admin == False:
		acc1 = Account.query.filter_by(id=data["from_account_id"]).filter_by(user_id=current_user.id).first()
		if not acc1:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not your account or account not found'
			}), 400
		if acc1.status == 'Inactive':
			return jsonify({
				'error': 'Bad Request',
				'message': 'Your account is inactive'
			}), 400	
		acc2 = Account.query.filter_by(id=data["to_account_id"]).first()
		if acc2.status == 'Inactive':
			return jsonify({
				'error': 'Bad Request',
				'message': 'Destination account is not active'
			}), 400	
		if acc1.balance <= 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400
		if acc1 == acc2:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Cant send to same account'
			}), 400
		t = Transaction( 
				date_transaction=datetime.today().strftime('%Y-%m-%d'),
				amount=data['amount'],
				desc=data.get('desc',"Transfer"),
				from_account_id=acc1.id,
				to_account_id=acc2.id,
				public_id=str(uuid.uuid4())
			)
		acc1.balance -= t.amount
		if acc1.balance < 50000:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not enough Balance'
			}), 400	
		acc2.balance += t.amount		
		db.session.add(t)
		db.session.commit()
		return {
			"message":"Success"
		}, 201

#History
@app.route('/history/') #Find berdasarkan nomor account
@token_required
def get_history(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# allow1 = auth(decode)[1]
	# user = User.query.filter_by(username=allow).filter_by(password=allow1).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401

	elif current_user:
		lst = []
		lst2 = []
		acc = Account.query.filter_by(user_id=current_user.id).all()
		for i in acc:
			lst.append(i.id)
		if not acc:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Not your account or wrong account'
			}), 400
		# i = Transaction.query.filter_by(from_account_id=acc.id).order_by(Transaction.date_transaction.desc()).all()
		for j in lst:
			acc2 = Transaction.query.filter_by(from_account_id=j).order_by(Transaction.date_transaction.desc()).all()
			for x in acc2:
				first_acc = Account.query.filter_by(id=x.from_account_id).first()
				last_acc = Account.query.filter_by(id=x.to_account_id).first()
				lst2.append({'transaction_date': x.date_transaction.strftime('%Y-%m-%d'), 'amount':x.amount, 'desc':x.desc,'from_account_id':first_acc.name_account,
						'to_account_id':last_acc.name_account})
		return jsonify(lst2),201
		

#DB Execute branch report total amount transaction by date
@app.route('/branch-report-transaction/', methods=['POST'])
@token_required
def branch_report_transaction(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
		data = request.get_json()
		create_view = db.engine.execute('''DROP VIEW IF EXISTS report; CREATE VIEW report AS SELECT b.name_branch as namebranch, SUM(t.amount) as samount, t."%s" as evdesc FROM transaction t INNER JOIN account a ON a.id = t.from_account_id INNER JOIN branch b ON b.id = a.branch_id WHERE (date_transaction BETWEEN '%s' AND '%s') GROUP BY namebranch, evdesc ORDER BY namebranch'''%("desc",data['start_date'], data['end_date'].strip()))
		result = db.engine.execute('''SELECT namebranch, SUM(Case When evdesc = 'Save' THEN samount ELSE 0 END),SUM(Case When evdesc = 'Withdraw'THEN samount ELSE 0 END)+SUM(Case When evdesc = 'Transfer'THEN samount ELSE 0 END) FROM report GROUP BY namebranch ''')
		x = []
		for y in result:
			x.append({'branch_name':y['namebranch'],'total_debit':y[1], 'total_credit':y[2]
				})
		return jsonify(x)
	elif current_user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Get data branch report total amount transaction by date
@app.route('/branch-report-transaction-get/', methods=['GET'])
@token_required
def branch_report_transaction_get(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
		# data = request.get_json()
		# create_view = db.engine.execute('''DROP VIEW IF EXISTS report; CREATE VIEW report AS SELECT b.name_branch as namebranch, SUM(t.amount) as samount, t."%s" as evdesc FROM transaction t INNER JOIN account a ON a.id = t.from_account_id INNER JOIN branch b ON b.id = a.branch_id WHERE (date_transaction BETWEEN '%s' AND '%s') GROUP BY namebranch, evdesc ORDER BY namebranch'''%("desc",data['start_date'], data['end_date'].strip()))
		result = db.engine.execute('''SELECT namebranch, SUM(Case When evdesc = 'Save' THEN samount ELSE 0 END),SUM(Case When evdesc = 'Withdraw'THEN samount ELSE 0 END)+SUM(Case When evdesc = 'Transfer'THEN samount ELSE 0 END) FROM report GROUP BY namebranch ''')
		x = []
		for y in result:
			x.append({'branch_name':y['namebranch'],'total_debit':y[1], 'total_credit':y[2]
				})
		return jsonify(x)
	elif current_user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#DB Execute per branch report total user,account,balance
@app.route('/branch-report-total/', methods=['GET'])
@token_required
def branch_report_total(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
					'message' : 'Check your login details.'
				}, 401
	if current_user.is_admin == True:
		result = db.engine.execute('''SELECT b.name_branch as namebranch, COUNT(u.id) as uid,COUNT(a.id) as countacc,SUM(a.balance) as sumbalance FROM account a INNER JOIN branch b ON b.id = a.branch_id INNER JOIN "%s" u ON a.user_id=u.id GROUP BY b.name_branch ORDER BY namebranch'''%("user"))
		x = []
		for y in result:
			x.append({'name_branch':y['namebranch'],'total_user':y['uid'], 'total_account':y['countacc'],'total_balance':y['sumbalance']})
		return jsonify(x)
	elif current_user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#DB Execute all branch report total user,account,balance
@app.route('/branch-all-report-total/', methods=['GET'])
@token_required
def branch_all_report_total(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
					'message' : 'Check your login details.'
				}, 401
	if current_user.is_admin == True:
		result = db.engine.execute('''SELECT COUNT(u.id) as uid,COUNT(a.id) as countacc,SUM(a.balance) as sumbalance FROM account a INNER JOIN branch b ON b.id = a.branch_id INNER JOIN "%s" u ON a.user_id=u.id'''%("user"))
		x = []
		for y in result:
			x.append({'total_user':y['uid'], 'total_account':y['countacc'],'total_balance':y['sumbalance']})
		return jsonify(x)
	elif current_user.is_admin == False:
		return {
			'message':'Youre unauthorize to do that.'
		},401

#Dormant Report
@app.route('/report-dormant/', methods=['GET'])
@token_required
def get_dormant_report(current_user):
	# decode = request.headers.get('Authorization')
	# allow = auth(decode)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
				'message' : 'Check your login details.'
			}, 401
	if current_user.is_admin == True:
		test = get_time() #get class get_time yang berisi rumus pengurangan -90 hari
		lsta = [] # untuk memasukkan semua account dari tabel account
		lstb = [] # untuk memasukkan semua data from_account_id dari tabel transaction
		lstc = [] # untuk memasukkan semua data yang tidak ada di dalam variabel lsta
		lstd = [] # untuk memasukkan data return
		t = Transaction.query.filter(Transaction.date_transaction.between(test[0],test[1])).all()
		acc = Account.query.all()
		for y in acc:
			lsta.append(y.id)
		for x in t:
			acc_ = Account.query.filter_by(id=x.from_account_id).first()
			lstb.append(acc_.id)
		for j in range(len(lsta)):
			if lsta[j] not in lstb:
				lstc.append(lsta[j])
		for q in lstc:
			t = Account.query.filter_by(id=q).first()
			trans = Transaction.query.filter_by(from_account_id=q).order_by(Transaction.id.desc()).first()
			time = datetime.today().strftime('%m') # mengambil data hari ini berdasarkan bulan
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
			lstd.append({'account_number': t.id, "dormant_duration_by_days": (time6 * 30)+time5, "account_name":t.name_account})
		return jsonify(lstd),201
	elif current_user.is_admin == False:
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
