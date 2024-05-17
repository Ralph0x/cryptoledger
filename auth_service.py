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
app.config['DATABASE_URL'] = os.getenv('DATABASE_URI')
app.config['JWT_ALGO'] = os.getenv('JWT_ALGORITHM', 'HS256')  # Specifying JWT Algorithm from .env, default to HS256
app.config['TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    hashed_password = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean)

class TokenBlacklist(db.Model):  # Model to store invalidated tokens
    id = db.Column(db.Integer, primary_key=True)
    revoked_token = db.Column(db.String(120), unique=True)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

def require_token(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('x-access-token')

        if not access_token:
            return jsonify({'message': 'Access token is missing!'}), 401

        try:
            payload = jwt.decode(access_token, app.config['SECRET_KEY'], algorithms=[app.config['JWT_ALGO']])
            if TokenBlacklist.query.filter_by(revoked_token=access_token).first():
                raise Exception('Access token has been invalidated')
            authenticated_user = User.query.filter_by(unique_id=payload['public_id']).first()
        except:
            return jsonify({'message': 'Access token is invalid!'}), 401

        return function(authenticated_user, *args, **kwargs)

    return decorated_function

@app.route('/user', methods=['POST'])
def register_user():
    registration_data = request.get_json()
    
    if User.query.filter_by(username=registration_data['name']).first():
        return jsonify({'message': 'User already exists.'}), 409

    new_password_hash = generate_password_hash(registration_data['password'], method='sha256')
    
    new_user = User(unique_id=str(uuid.uuid4()), username=registration_data['name'], hashed_password=new_password_hash, is_admin=False)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'New user registered!'})

@app.route('/login')
def authenticate_user():
    credentials = request.authorization
    
    if not credentials or not credentials.username or not credentials.password:
        return make_response('Credentials missing', 400, {'WWW-Authenticate': 'Basic realm="Authentication required!"'})
    
    user = User.query.filter_by(username=credentials.username).first()
    
    if not user:
        return make_response('User not found', 404, {'WWW-Authenticate': 'Basic realm="Authentication required!"'})
    
    if check_password_hash(user.hashed_password, credentials.password):
        token_payload = {'public_id': user.unique_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}
        generated_token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGO'])
        
        return jsonify({'token': generated_token})
    
    return make_response('Invalid credentials', 403, {'WWW-Authenticate': 'Basic realm="Authentication required!"'})

@app.route('/logout', methods=['POST'])
@require_token
def invalidate_token(authenticated_user):
    access_token = request.headers.get('x-access-token')
        
    if access_token:
        invalidated_token = TokenBlacklist(revoked_token=access_token)
        invalidated_token.save()
        return jsonify({'message': 'Access token has been invalidated'}), 200
    
    return jsonify({'message': 'Access token is missing!'}), 401

@app.route('/dashboard')
@require_token
def user_dashboard(authenticated_user):
    return jsonify({'message': 'Dashboard accessed successfully'})

@app.route('/promote/<unique_id>', methods=['PUT'])
@require_token
def promote_user_to_admin(authenticated_user, unique_id):
    if not authenticated_user.is_admin:
        return jsonify({'message': 'Insufficient permissions to execute this function!'}), 403

    user_to_promote = User.query.filter_by(unique_id=unique_id).first()

    if not user_to_promote:
        return jsonify({'message': 'User not found!'}), 404
    
    user_to_promote.is_admin = True
    db.session.commit()
    
    return jsonify({'message': 'User has been promoted to admin status.'})

if __name__ == '__main__':
    db.create_all()  # Ensure all database tables are created
    app.run(debug=True)