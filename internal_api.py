from flask import Flask, render_template,request, redirect, url_for, session,  flash,request, jsonify,abort
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import random
import os



app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://retro_user:1234@10.0.0.21:3316/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/', methods=['GET'])
def root():
    return "Welcome. Please be advised that this area is for authorized Development Team personnel. Unauthorized access is strictly prohibited."

@app.route('/dogs', methods=['POST', 'GET'])
def dogs():
    img_url = None

    if request.method == "POST":
        api_url = request.form.get("api")

        try:
            response = requests.get(api_url) 
        except:
            return "Faild to reach API"

        if response.ok and "message" in response.json():
            json = response.json()
            img_url = json["message"]
            return render_template("dog.html", img_src=img_url)
        else:
            return response.text, response.status_code
    return render_template("dog.html")


@app.route('/qun', methods=['GET'])
def qun():
    return render_template("qun.html")



@app.route('/qun/buy', methods=['POST', 'GET'])
def buy_qun():

    dev_token = request.args.get('dev_token')
    
    if dev_token == None:
        return "missiong parmmaters: dev_token"
    
    token_is_vaild =  db.session.execute(text("SELECT dev_token FROM users WHERE dev_token = :dev_token"), {"dev_token": dev_token}).fetchone()
    if token_is_vaild != None:
        
        dev_info = db.session.execute(text("SELECT * FROM users WHERE dev_token = :dev_token"), {"dev_token": dev_token}).fetchone()
        dev_have = db.session.execute(text("SELECT * FROM cart_items WHERE user_id = :user_id AND product_id = 99"), {"user_id": dev_info[0]}).fetchone()

        if dev_have == None:

            db.session.execute(
                text("INSERT INTO cart_items (user_id, product_id) VALUES(:user_id, 99)"),
                {'user_id': dev_info[0]}
            )
            

            db.session.execute(
                text("UPDATE users SET does_own_qun = 1 WHERE username = :username"),
                {'username': dev_info[0]}
            )
            
            db.session.commit()
            
            return f"Add quantum computer to dev {dev_info[0]} cart"
        else:
            return "This item is already in your cart."
    else:
        return "dev token not vaild"


if __name__ == "__main__":
    secret_port = random.randrange(5000, 8000)
    print(f"Internal API starting on secret random port: {secret_port}")
    app.run(debug=True, port=secret_port, host="0.0.0.0")