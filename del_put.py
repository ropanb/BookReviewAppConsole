from flask import Flask, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required
import os

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY')
	SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

app = Flask(__name__)
db = SQLAlchemy()
#login_manager = LoginManager()
#login_manager.login_view = 'users.login'
#login_manager.login_message_category = 'info'
db.init_app(app)
#login_manager.init_app(app)
app.config.from_object(Config)

#@login_manager.user_loader
#def load_user(user_id):
#    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
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

@app.route('/login', methods = ['GET','POST'])
def login():
#	if current_user.is_authenticated:
#		return "Success"
	username = list(request.json.keys())[0]
#	passwordhash = list(request.json.values())[0]
	user = User.query.filter_by(username=username).first()
#	if user and (user.password == passwordhash):
	    #login_user(user)
	return jsonify(user.id), 200
#	else:
#		return "Failed"

@app.route('/records/<string:bookname>/<int:user_id>', methods=['GET'])
#@login_required
def get_method(bookname,user_id):
	if bookname == "all":
		readinglist = Readinglist.query.filter_by(user_id=user_id).all()
	else:	
		readinglist = Readinglist.query.filter_by(bookname=bookname, author=user_id).all()
	book = {}
	for alist in readinglist:
		book[alist.id] = alist.bookname
	return book


@app.route('/records/delete/<int:id>', methods=['DELETE'])
#@login_required
def del_method(id):
	response= Readinglist.query.get_or_404(id)
	db.session.delete(response)
	db.session.commit()
	return "Success"

@app.route('/records/add/<int:user_id>', methods=['POST'])
#@login_required
def post_method(user_id):
	if not request:
		return jsonify({'error':'the new record is incorrect'}), 400
	isbn = int(request.json["isbn"])
	alist = Readinglist(bookname=request.json["bookname"], review = request.json["review"], 
            isbn = isbn,libid = request.json["libid"],user_id=user_id)
	db.session.add(alist)
	db.session.commit()
	return jsonify({'Success':'the new record is added'}), 200


@app.route('/records/update/<int:id>', methods=['PUT'])
#@login_required
def put_method(id):
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