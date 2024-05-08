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
    if not data or not data.get('name'):
        return jsonify({'error': 'Missing name'}), 400
    try:
        new_portfolio = Portfolio(name=data['name'])
        db.session.add(new_portfolio)
        db.session.commit()
        return jsonify({'message': 'Portfolio created', 'id': new_portfolio.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/portfolio/<int:portfolio_id>/transaction', methods=['POST'])
def add_transaction(portfolio_id):
    data = request.json
    if not data or not data.get('cryptocurrency') or not data.get('amount'):
        return jsonify({'error': 'Missing cryptocurrency or amount'}), 400
    try:
        new_transaction = Transaction(
            cryptocurrency=data['cryptocurrency'],
            amount=data['amount'],
            portfolio_id=portfolio_id
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction added'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/portfolio/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    try:
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        portfolio_data = {'name': portfolio.name, 'transactions': []}
        for transaction in portfolio.transactions:
            portfolio_data['transactions'].append({
                'cryptocurrency': transaction.cryptocurrency,
                'amount': transaction.amount
            })
        return jsonify(portfolio_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/market/<string:cryptocurrency>', methods=['GET'])
def get_market_data(cryptocurrency):
    api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={cryptocurrency}&vs_currencies=usd"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # This will raise an exception for 4XX/5XX responses
        data = response.json()
        return jsonify(data[cryptocurrency])
    except requests.RequestException as e:
        return jsonify({'message': 'Failed to retrieve data', 'error': str(e)}), 500

@app.route('/analysis/<int:portfolio_id>', methods=['GET'])
def perform_analysis(portfolio_id):
    try:
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        total_value = 0
        for transaction in portfolio.transactions:
            api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={transaction.cryptocurrency}&vs_currencies=usd"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                total_value += data[transaction.cryptocurrency]['usd'] * transaction.amount
            else:
                return jsonify({'error': f"Failed to retrieve market data for {transaction.cryptocurrency}."}), 500
        return jsonify({'total_value_usd': total_value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)