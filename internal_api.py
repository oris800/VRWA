from flask import Flask, render_template,request, redirect, url_for, session,  flash,request, jsonify,abort
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import random




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://retro_user:1234@10.0.0.15/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.before_request
def limit_remote_addr():
    if request.remote_addr != '127.0.0.1':
        abort(403)  

@app.route('/', methods=['GET'])
def chackstock():
    return "hello?"

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

@app.route('/add', methods=['POST', 'GET'])
def add():
    user_name = request.args.get('user')
    cash = request.args.get('cash')
    secret_token = request.args.get('token')

    if user_name == None and cash == None and secret_token == None:
        return "missiong parmmaters: user,cash,token"
    admin_row = db.session.execute(text("SELECT * FROM admins where name = 'admin'")).fetchone()
    
    admin_fruit = admin_row[3]
    
    user_id = db.session.execute(text(f"SELECT * FROM users WHERE username = '{user_name}'")).fetchone()
    
    user_cash = user_id[5]

    if user_id == None:
        return "user has not found"
    if secret_token != admin_fruit:
        return "secret token not match"


    if secret_token == admin_fruit:
        if user_cash + int(cash) < 100000:            
            print(user_cash + int(cash))
            db.session.execute(text(f"UPDATE users SET money = money + {int(cash)} WHERE id = {user_id[0]}"))
            db.session.commit()
            return f"add {cash} to user: {user_name}"
        else:
            return "user cant have more than: " + str(100000)
    else:
        return "secret token not match"
    



@app.route('/qun/buy', methods=['POST', 'GET'])
def buy_qun():
    user_name = request.args.get('user')
    secret_token = request.args.get('token')
    
    admin_row = db.session.execute(text("SELECT * FROM admins where name = 'admin'")).fetchone()
    admin_fruit = admin_row[3]

    user_row = db.session.execute(text(f"SELECT * FROM users WHERE username = '{user_name}'")).fetchone()

    if secret_token == None and user_name == None:
        return "missiong parmmaters: user,token"

    print("input: ",secret_token,"admin: ",admin_fruit)
    if user_row is None:
        return "user is not internal"

    is_internal_user = user_row[6]
    print(is_internal_user)

    if secret_token == admin_fruit and is_internal_user: 
        user_id = db.session.execute(text(f"SELECT id FROM users WHERE username = '{user_name}'")).fetchone()
        user_have = db.session.execute(text("SELECT * FROM cart_items WHERE user_id = :user_id AND product_id = 99"), {"user_id": user_id[0]}).fetchone()
        print(user_have)
        if user_have == None:
            db.session.execute(text(f"INSERT INTO cart_items (user_id , product_id) VALUES({user_id[0]},99) "))
            db.session.commit()
            return f"add to cart to user: {user_name}"
        else:
            return "you cant buy item twise"
    else:
        return "secret token not match"
    




    


if __name__ == "__main__":
    app.run(debug=True, port=random.randrange(5000, 8000), host="0.0.0.0")