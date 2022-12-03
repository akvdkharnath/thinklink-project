import requests
import os
import json

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify  
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_mail import Mail, Message
from sqlalchemy import func
from datetime import datetime, date

# loading .env
load_dotenv()

# creating app and adding configuration for mailing and database servics 
app = Flask(__name__)  
app.config['MAIL_SERVER']= os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False 
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")

# Creating an SQLAlchemy instance and Mail instance
db = SQLAlchemy(app)
mail = Mail(app)

# Models
class BitCoinPrice(db.Model):
    __tablename__ = "bitcoin_price"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, unique=False, nullable=False, default= datetime.utcnow)
    price = db.Column(db.Float, nullable=False) 

# PREREQUIRED functions

def data_collector():
    """Function responsible for fetching bitcoin prices from coingecko using API and inserting into database"""

    # using https://api.coingecko.com/api/v3/coins/list API listed in coingecko API document need to find id to bitcoin
    crypto_id = "bitcoin"
    # using https://api.coingecko.com/api/v3/simple/supported_vs_currencies API listed in coingecko API document need to find currency code to get prices in USD currency
    currencie_id = "usd"
    
    # API get request to coingecko to feach current prices 
    URL = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies={currencie_id}"
    response = requests.request("GET", URL)
    data = json.loads(response.text)
    try:
        price = data["bitcoin"]["usd"]
        max_price = int(os.getenv("MAX", "0"))
        min_price = int(os.getenv("MIN", "0"))
        
        if price < min_price:
            # if current price is less than min price sending email of Bitcoin drop alert
            subject = "Bitcoin drop alert"
            body = f"Hi it looks its good time to buy bit coin it droped to {price} USD"
            send_warrining_mails(subject, body)
        elif price > max_price:
            # if current price is more than max price sending email of Bitcoin rise alert
            subject = "Bitcoin rise alert"
            body = f"Hi it looks its good time to sell bit coin it hiked to {price} USD"
            send_warrining_mails(subject, body)
        
        data_setter(price)
    except Exception as e:
        print("In Exception")
        print(e)
        pass

def send_warrining_mails(subject, body):
    """ Function responsible for sending email usinf SMTP serive """
    msg = Message(
                subject,
                sender ='akvdkharnath@gmail.com',
                recipients = [os.getenv("EMAIl")]
               )
    msg.body = body
    
    with app.app_context():
        mail.send(msg)
        print("Mail sent")

def data_setter(price):
    """Function inserts latest bitcoin price into bitcoin_price table"""
    price_data = BitCoinPrice(price = price)
    with app.app_context():
        db.session.add(price_data)
        db.session.commit()

# scheduling background scheduler to call data_collector function for every 30 seconds 
sched = BackgroundScheduler(daemon=True)
sched.add_job(data_collector,'interval',seconds=30)
sched.start()

@app.route("/api/prices/btc")  
def get_prices_list():  
    args = request.args.to_dict()
    
    # assigning default values if offset and limit are not provided
    if "offset" not in args:
        args["offset"] = 0
    
    if "limit" not in args:
        args["limit"] = 10
    
    day, month, year = list(map(int, args["date"].split("-")))
    transaction_date = date(year, month, day)
    
    query = db.session.query(BitCoinPrice).filter(func.date(BitCoinPrice.timestamp) == transaction_date).limit(args["limit"]).offset(args["offset"])
    
    #transaction_date = date(2021, 8, 25)
    #transactions = Transactions.query.filter(func.date(Transactions.datetime_posted) == transaction_date).all()
    
    result = []
    for record in query.all():
        temp_record = record.__dict__
        temp_record["timestamp"] = str(temp_record["timestamp"])
        temp_record["coin"] = "btc"
        temp_record.pop('_sa_instance_state', None)
        temp_record.pop('id', None)
        result.append(temp_record)
    
    response = {}
    response["url"] = f"<http://localhost:8000/api/prices/btc?date={args['date']}&offset={args['offset']}&limit={args['limit']}>"
    response["next"] = f"<http://localhost:8000/api/prices/btc?date={args['date']}&offset={args['limit']}&limit={args['limit']}>"
    response["count"] = len(result)
    response["count"] = result
    return jsonify(response)
 
if __name__ == "__main__": 
    with app.app_context():
        db.create_all()
    app.run(host ='0.0.0.0', port = 5000, debug = True)  