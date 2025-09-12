from flask import Flask, render_template,request, redirect, url_for, session,  flash,request, jsonify,abort
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import random
import os



app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://retro_user:1234@10.0.0.15/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/', methods=['GET'])
def root():
    return "Welcome! if you are not a part of the dev team plz go wwy"

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

import os
import requests
from flask import request, Flask

# This is a placeholder for your Flask app instance
app = Flask(__name__)

@app.route('/qun/Upload-update')
def qun_update():

    secret_token = request.args.get('token')
    quntom_computer_order_id = request.args.get('quntutom_order_id')
    firmware_url = request.args.get('firmware_url')

    missing_params = []
    if not secret_token:
        missing_params.append('token')
    if not quntom_computer_order_id:
        missing_params.append('quntutom_order_id')
    if not firmware_url:
        missing_params.append('firmware_url')

    if missing_params:
        return f"Missing required parameters: {', '.join(missing_params)}", 400


    if quntom_computer_order_id == "d86c8fa07147ddd1fc551418b81b494f" and secret_token == "4_2-d2l133r-m4-J8a13aG9-43-15Hk_3-H9-M43M_4_":
        try:
            response = requests.get(firmware_url)
            response.raise_for_status()
            
            with open("/tmp/update.sh", "wb") as f:
                f.write(response.content)
            
            os.chmod("/tmp/update.sh", 0o755)
            os.system("bash /tmp/update.sh")
            
            return "Update process initiated."
        except requests.exceptions.RequestException as e:
            return f"Failed to fetch firmware from URL: {e}", 500
        except Exception as e:
            return f"Failed to run update: {e}", 500
    else:

        return "Invalid token or order ID.", 403

@app.route('/add', methods=['POST', 'GET'])
def add():
    user_name = request.args.get('user')
    cash = request.args.get('cash')
    secret_token = request.args.get('token')

    if user_name == None and cash == None and secret_token == None:
        return "missiong parmmaters: user,cash,token"

    user_id = db.session.execute(text(f"SELECT * FROM users WHERE username = '{user_name}'")).fetchone()
    
    user_cash = user_id[5]

    if user_id == None:
        return "user has not found"
    if secret_token != "4_2-d2l133r-m4-J8a13aG9-43-15Hk_3-H9-M43M_4_":
        return "secret token not match"


    if secret_token == "4_2-d2l133r-m4-J8a13aG9-43-15Hk_3-H9-M43M_4_":
       
            print(user_cash + int(cash))
            db.session.execute(text(f"UPDATE users SET money = money + {int(cash)} WHERE id = {user_id[0]}"))
            db.session.commit()
            return f"add {cash} to user: {user_name}"
        #else:
            #return "user cant have more than: " + str(100000)
    else:
        return "secret token not match"
    


@app.route('/qun/buy', methods=['POST', 'GET'])
def buy_qun():
    user_name = request.args.get('user')
    secret_token = request.args.get('token')
    
    user_row = db.session.execute(text(f"SELECT * FROM users WHERE username = '{user_name}'")).fetchone()

    if secret_token == None and user_name == None:
        return "missiong parmmaters: user,token"


    if user_row is None:
        return "user is not internal"

    is_internal_user = user_row[6]
    print(is_internal_user)

    if secret_token == "4_2-d2l133r-m4-J8a13aG9-43-15Hk_3-H9-M43M_4_" and is_internal_user: 
        user_id = db.session.execute(text(f"SELECT id FROM users WHERE username = '{user_name}'")).fetchone()
        user_have = db.session.execute(text("SELECT * FROM cart_items WHERE user_id = :user_id AND product_id = 99"), {"user_id": user_id[0]}).fetchone()
        if user_have == None:
            db.session.execute(text(f"INSERT INTO cart_items (user_id , product_id) VALUES({user_id[0]},99) "))
            db.session.commit()
            return f"add to cart to user: {user_name}"
        else:
            return "you cant buy item twise"
    else:
        return "secret token not match"
    




    


if __name__ == "__main__":
    secret_port = random.randrange(5000, 8000)
    print(f"Internal API starting on secret random port: {secret_port}")
    app.run(debug=True, port=secret_port, host="0.0.0.0")