import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import jwt
import uuid
import datetime

load_dotenv()  # Load environment variables

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')  # New: JWT Algorithm from .env, default to HS256
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

class RevokedToken(db.Model):  # New: Model to store revoked tokens
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(120), unique=True)
    
    def add(self):
        db.session.add(self)
        db.session.commit()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
            if RevokedToken.query.filter_by(token=token).first():
                raise Exception('Token has been revoked')
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if User.query.filter_by(name=data['name']).first():
        return jsonify({'message': 'User already exists.'}), 409

    hashed_password = generate_password_hash(data['password'], method='sha256')
    
    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'New user created!'})

@app.route('/login')
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return make_response('Missing credentials', 400, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(name=auth.username).first()
    
    if not user:
        return make_response('User not found', 404, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])
        
        return jsonify({'token': token})
    
    return make_response('Invalid credentials', 403, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/logout', methods=['POST'])  # New: Logout route
@token_required
def logout(current_user):
    token = None
    if 'x-access-token' in request.headers:
        token = request.headers['x-access-token']
        
    if token:
        blacklisted_token = RevokedToken(token=token)  # Invalidate token
        blacklisted_token.add()
        return jsonify({'message': 'Token has been revoked'}), 200
    
    return jsonify({'message': 'Token is missing!'}), 401

@app.route('/dashboard')
@token_required
def dashboard(current_user):
    return jsonify({'message': 'Dashboard accessed successfully'})

@app.route('/promote/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    # Ensure only admin can promote users
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform that function!'}), 403

    user_to_promote = User.query.filter_by(public_id=public_id).first()

    if not user_to_promote:
        return jsonify({'message': 'No user found!'}), 404
    
    user_to_promote.admin = True
    db.session.commit()
    
    return jsonify({'message': 'The user has been promoted to admin.'})

if __name__ == '__main__':
    db.create_all()  # Ensure all tables are created
    app.run(debug=True)