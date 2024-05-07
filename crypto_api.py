from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///:memory:')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    transactions = db.relationship('Transaction', backref='portfolio', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cryptocurrency = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)

db.create_all()

@app.route('/portfolio', methods=['POST'])
def create_portfolio():
    data = request.json
    new_portfolio = Portfolio(name=data['name'])
    db.session.add(new_portfolio)
    db.session.commit()
    return jsonify({'message': 'Portfolio created', 'id': new_portfolio.id}), 201

@app.route('/portfolio/<int:portfolio_id>/transaction', methods=['POST'])
def add_transaction(portfolio_id):
    data = request.json
    new_transaction = Transaction(
        cryptocurrency=data['cryptocurrency'],
        amount=data['amount'],
        portfolio_id=portfolio_id
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction added'}), 201

@app.route('/portfolio/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio_data = {'name': portfolio.name, 'transactions': []}
    for transaction in portfolio.transactions:
        portfolio_data['transactions'].append({
            'cryptocurrency': transaction.cryptocurrency,
            'amount': transaction.amount
        })
    return jsonify(portfolio_data)

@app.route('/market/<string:cryptocurrency>', methods=['GET'])
def get_market_data(cryptocurrency):
    api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={cryptocurrency}&vs_currencies=usd"
    response = requests.get(api_url)
    if response.status_code != 200:
        return jsonify({'message': 'Failed to retrieve data'}), 500
    data = response.json()
    return jsonify(data[cryptocurrency])

@app.route('/analysis/<int:portfolio_id>', methods=['GET'])
def perform_analysis(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    total_value = 0
    for transaction in portfolio.transactions:
        api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={transaction.cryptocurrency}&vs_currencies=usd"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            total_value += data[transaction.cryptocurrency]['usd'] * transaction.amount
    return jsonify({'total_value_usd': total_value})

if __name__ == '__main__':
    app.run(debug=True)