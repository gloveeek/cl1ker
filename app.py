from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import logging
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://clicker_user:new_password@localhost/clicker_game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referral_code = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        telegram_id = data['telegram_id']
        username = data['username']
        existing_user = User.query.filter_by(telegram_id=telegram_id).first()
        if existing_user is None:
            new_user = User(telegram_id=telegram_id, username=username)
            db.session.add(new_user)
            db.session.commit()
            return jsonify(message="User registered successfully"), 201
        return jsonify(message="User already registered"), 200
    except Exception as e:
        app.logger.error(f"Error in /register: {str(e)}")
        return jsonify(error=str(e)), 500

@app.route('/click', methods=['POST'])
def click():
    try:
        data = request.json
        telegram_id = data['telegram_id']
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if user:
            user.balance += 1
            db.session.commit()
            return jsonify(balance=user.balance), 200
        return jsonify(message="User not found"), 404
    except Exception as e:
        app.logger.error(f"Error in /click: {str(e)}")
        return jsonify(error=str(e)), 500

@app.route('/balance/<int:telegram_id>', methods=['GET'])
def balance(telegram_id):
    try:
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if user:
            return jsonify(balance=user.balance), 200
        return jsonify(message="User not found"), 404
    except Exception as e:
        app.logger.error(f"Error in /balance: {str(e)}")
        return jsonify(error=str(e)), 500

@app.route('/btc-price', methods=['GET'])
def btc_price():
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT')
        price = response.json()['price']
        return jsonify(price=price), 200
    except Exception as e:
        app.logger.error(f"Error in /btc-price: {str(e)}")
        return jsonify(error=str(e)), 500

@app.route('/trade', methods=['POST'])
def trade():
    try:
        data = request.json
        user_id = data['user_id']
        amount = data['amount']
        price = data['price']
        user = User.query.get(user_id)
        if user and user.balance >= amount:
            user.balance -= amount
            new_trade = Trade(user_id=user_id, amount=amount, price=price)
            db.session.add(new_trade)
            db.session.commit()
            return jsonify(message="Trade successful"), 200
        return jsonify(message="Trade failed: insufficient balance or user not found"), 400
    except Exception as e:
        app.logger.error(f"Error in /trade: {str(e)}")
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
