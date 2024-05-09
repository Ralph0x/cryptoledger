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
    cryptocurrency_name = db.Column(db.String(50), nullable=False)
    trade_amount = db.Column(db.Float, nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)

db.create_all()

@app.route('/portfolio', methods=['POST'])
def create_portfolio_endpoint():
    request_data = request.json
    if not request_data or not request_data.get('name'):
        return jsonify({'error': 'Missing name'}), 400
    try:
        new_portfolio = Portfolio(name=request_data['name'])
        db.session.add(new_portfolio)
        db.session.commit()
        return jsonify({'message': 'Portfolio created successfully', 'id': new_portfolio.id}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': str(error)}), 500

@app.route('/portfolio/<int:portfolio_id>/transaction', methods=['POST'])
def add_transaction_endpoint(portfolio_id):
    request_data = request.json
    if not request_data or not request_data.get('cryptocurrency') or not request_data.get('amount'):
        return jsonify({'error': 'Missing cryptocurrency or amount information'}), 400
    try:
        new_transaction = Transaction(
            cryptocurrency_name=request_data['cryptocurrency'],
            trade_amount=request_data['amount'],
            portfolio_id=portfolio_id
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': 'Transaction added successfully'}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': str(error)}), 500

@app.route('/portfolio/<int:portfolio_id>', methods=['GET'])
def get_portfolio_transactions(portfolio_id):
    try:
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        portfolio_details = {'name': portfolio.name, 'transactions': []}
        for transaction in portfolio.transactions:
            portfolio_details['transactions'].append({
                'cryptocurrency': transaction.cryptocurrency_name,
                'amount': transaction.trade_amount
            })
        return jsonify(portfolio_details)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@app.route('/market/<string:cryptocurrency>', methods=['GET'])
def get_cryptocurrency_market_data(cryptocurrency):
    market_data_url = f"https://api.coingecko.com/api/v3/simple/price?ids={cryptocurrency}&vs_currencies=usd"
    try:
        market_response = requests.get(market_data_url)
        market_response.raise_for_status()  # Raises exception for 4XX/5XX responses
        price_data = market_response.json()
        return jsonify(price_data[cryptocurrency])
    except requests.RequestException as error:
        return jsonify({'message': 'Failed to retrieve data', 'error': str(error)}), 500

@app.route('/analysis/<int:portfolio_id>', methods=['GET'])
def perform_portfolio_analysis(portfolio_id):
    try:
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        total_usd_value = 0
        for transaction in portfolio.transactions:
            market_data_url = f"https://api.coingecko.com/api/v3/simple/price?ids={transaction.cryptocurrency_name}&vs_currencies=usd"
            market_response = requests.get(market_data_url)
            if market_response.status_code == 200:
                price_data = market_response.json()
                total_usd_value += price_data[transaction.cryptocurrency_name]['usd'] * transaction.trade_amount
            else:
                return jsonify({'error': f"Failed to retrieve market data for {transaction.cryptocurrency_name}."}), 500
        return jsonify({'total_value_usd': total_usd_value})
    except Exception as error:
        return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True)