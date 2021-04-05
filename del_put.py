from flask import Flask, request, jsonify, json, make_response
from flask_sqlalchemy import SQLAlchemy
import os, jwt, datetime, uuid
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Initialising the app and the configuration variables
class Config:
	SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

app = Flask(__name__)
db = SQLAlchemy()
db.init_app(app)
app.config['SECRET_KEY']='Th1s1ss3cr3t'
app.config.from_object(Config)

# Creating the table objects based on the databse schema
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    readinglist = db.relationship('Readinglist', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}',{self.id}.'{self.email}')"

class Readinglist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookname = db.Column(db.String(100), nullable=False)
    review = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.Integer, nullable=False)
    libid = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ReadingList('{self.bookname}')"

#Setting the routes
# Registration functionality. Uses hashing with sha256 method
@app.route('/register', methods=['GET', 'POST'])
def signup_user():
	data = request.get_json()  
	hashed_password = generate_password_hash(data['password'], method='sha256')
	new_user = User(username=data['name'], email = data['email'], password=hashed_password) 
	db.session.add(new_user)  
	db.session.commit()    
	return jsonify({'message': 'registered successfully'})

# Creating the decorator Function to be added to ensure token is available when accessing the API
# HS256 algorith used for token encoding and decoding
def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = None
		if 'Bearer' in request.headers:
			token = request.headers["Bearer"]
		if not token:
			return jsonify({'message': 'a valid token is missing'})		
		data = jwt.decode(token, "secret",algorithms="HS256")
		current_user = User.query.filter_by(id=data['public_id']).first()
		return f(current_user, *args, **kwargs)
	return decorator

# Login function. Uses hashing with sha256 method and token generator HS256 algorithm
@app.route('/login', methods = ['GET','POST'])
def login():
	auth = request.authorization

	if not auth or not auth.username or not auth.password:
		return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
	user = User.query.filter_by(username=auth.username).first()
	if check_password_hash(user.password, auth.password):
		token = jwt.encode({'public_id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, "secret",algorithm="HS256")
		return jsonify({'token' : token}) 
	else:
		return "Failed"

# GET method to fetch all the books or a particular book reviewed by the user, 
@app.route('/records/<string:bookname>', methods=['GET'])
@token_required
def get_method(current_user,bookname):
	if bookname == "all":
		readinglist = Readinglist.query.filter_by(author=current_user).all()
	else:	
		readinglist = Readinglist.query.filter_by(bookname=bookname, author=current_user).all()
	book = {}
	for alist in readinglist:
		book[alist.id] = alist.bookname
	return jsonify(book)

# Delete method to delete a particular review
@app.route('/records/delete/<int:id>', methods=['DELETE'])
@token_required
def del_method(current_user,id):
	response= Readinglist.query.get_or_404(id)
	db.session.delete(response)
	db.session.commit()
	return "Success"

# POST method to create a new book review
@app.route('/records/add', methods=['POST'])
@token_required
def post_method(current_user):
	if not request:
		return jsonify({'error':'the new record is incorrect'}), 400
	isbn = int(request.json["isbn"])
	alist = Readinglist(bookname=request.json["bookname"], review = request.json["review"], 
		isbn = isbn,libid = request.json["libid"],user_id=current_user.id)
	db.session.add(alist)
	db.session.commit()
	return jsonify({'Success':'the new record is added'}), 200

# PUT method to delete a particular review
@app.route('/records/update/<int:id>', methods=['PUT'])
@token_required
def put_method(current_user,id):
	readinglist = Readinglist.query.get_or_404(id)
	if not request:
		return jsonify({'error':'the new record is incorrect'}), 400
	readinglist.id = id
	stringId = str(id)
	readinglist.review = request.json[stringId]
	db.session.commit()
	return "Success!"

if __name__ == "__main__":
	app.run(debug=True)