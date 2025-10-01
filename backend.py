# CORRECTED AND CONSOLIDATED IMPORTS
# --- Flask Imports ---
from flask import (Flask, render_template, request, redirect, url_for, 
                   session, flash, jsonify, Response, make_response, send_from_directory)

# --- Database Imports ---
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# --- Standard Library Imports ---
from datetime import datetime, timedelta, timezone
import random 
import os
import time
import contextlib
import traceback
import io
import subprocess 
import base64

# --- Third-Party Library Imports ---
import requests
from Crypto.Hash import MD5, MD2
app = Flask(__name__)

app.secret_key = "931484461332a6e568a183515f4e9a5c898684724a2cbe5391d1e67e54a88941"

db_user = os.getenv('DB_USER', 'retro_user')
db_password = os.getenv('DB_PASSWORD', '1234')
db_host = os.getenv('DB_HOST', 'localhost') #
db_name = os.getenv('DB_NAME', 'app')
db_port = 3306 

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)





def encode_to_base64(text):
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def decode_from_base64(encoded_text):
    try:
        return base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')
    except Exception:
        return None 


@app.route('/robots.txt')
def robots_txt():

    try:
        return send_from_directory(app.root_path, 'robots.txt')
    except FileNotFoundError:

        return "File not found", 404

@app.route('/')
def home():
    featured_product_query = text("SELECT * FROM products WHERE id = 2")
    featured_product = db.session.execute(featured_product_query).fetchone()
    
    products = db.session.execute(text("SELECT * FROM products WHERE show_on_page = 1")).fetchall()    
    
    if "username" in session:
         return render_template('index.html',  
                           products=products,
                           featured_product=featured_product,username=session["username"])
    else:
         return render_template('index.html',  
                           products=products,
                           featured_product=featured_product)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return 'Username and password are required', 400
        
        hashed_input_password = MD5.new(password.encode()).hexdigest()
        
        query_string = "SELECT * FROM users WHERE username = :username AND password = :password"
        query = text(query_string)
        result = db.session.execute(query, {'username': username, 'password': hashed_input_password}).fetchone()

        if result:
            session.clear() 
            session['username'] = username
            response = make_response('Login successful', 200)

            response.headers['X-User-ID'] = result.id
            response.headers['X-Redirect-Url'] = url_for('user_page')
            
            return response
        else:
            return 'Invalid username or password', 401


@app.route('/reset', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':

        if 'new_password' in request.form and session.get('can_reset_password'):
            
            username = session.get('user_to_reset')
            
            if not username:
                flash("An error occurred. Please start the password reset process again.", "error")
                return redirect(url_for('reset'))

            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password == confirm_password:
                hashed_new_password = MD5.new(new_password.encode()).hexdigest()


                db_query = "UPDATE users SET password = :password WHERE username = :username"
                db.session.execute(text(db_query), {'password': hashed_new_password, 'username': username})
                db.session.commit()

                # נקה את משתני ה-session לאחר השימוש כדי למנוע שימוש חוזר
                session.pop('can_reset_password', None)
                session.pop('user_to_reset', None)

                flash("Password has been reset successfully!", "success")
                return redirect(url_for('login_page'))
            else:
                message = {
                    "text": "Passwords do not match",
                    "color": "red"
                }
                return render_template('reset.html', message=message, allow_password_reset=True, username=username)

        elif 'security_answer' in request.form:
            username = request.form.get('username')
            submitted_answer = request.form.get('security_answer')
            
            db_query = "SELECT security_answer FROM users WHERE username = :username"
            result = db.session.execute(text(db_query), {'username': username}).fetchone()
            
            if result and submitted_answer.lower() == result[0].lower():

                session['can_reset_password'] = True
                session['user_to_reset'] = username  
                
                message = {
                    "text": "Security answer is correct.",
                    "color": "green"
                }
                return render_template('reset.html', message=message, allow_password_reset=True, username=username)
            else:
                message = {
                    "text": "Security answer is wrong.",
                    "color": "red"
                }
                db_query = "SELECT security_question FROM users WHERE username = :username"
                result_question = db.session.execute(text(db_query), {'username': username}).fetchone()
                if result_question:
                    return render_template('reset.html', username=username, security_question=result_question[0], message=message)
                else: 
                    flash("User not found.", "error")
                    return redirect(url_for('reset'))


        elif 'username' in request.form:
            username = request.form.get('username')
            db_query = "SELECT security_question FROM users WHERE username = :username"
            result = db.session.execute(text(db_query), {'username': username}).fetchone()

            if result:
                return render_template('reset.html', username=username, security_question=result[0])
            else:
                message = {
                    "text": "The user was not found.",
                    "color": "red"
                }
                return render_template('reset.html', message=message)

    return render_template('reset.html')




#-----------------------------------------
@app.route('/login/check', methods=['POST'])
def check_user():
    id_from_request = request.form.get('id')

    if id_from_request is None or id_from_request == '':
        return "Error: No ID provided.", 400

    db_query = f"SELECT * FROM users WHERE id = {id_from_request}"
    
    try:
        result = db.session.execute(text(db_query)).fetchone()
        
        if result is None:
            return "False"  
        else:
            return "True"
    except Exception as e:
        return "500 INTERNAL SERVER ERROR", 500
#-----------------------------------------

@app.route('/user', methods=['GET', 'POST'])
def user_page():
    if "admin_name" in session:
        return redirect(url_for('admin_panal'))
        
    if "username" not in session:
        return "You are not an authorized user. Please <a href='/login'>login</a>.", 401

    username = session["username"]
    user_info = db.session.execute(text("SELECT * FROM users WHERE username = :name"), {'name': username}).fetchone()
    
    is_dev = user_info[7] == 1
    user_owns_quantum = user_info[10] == 1

    transactions = []
    if is_dev:
        transactions_query = text("""
            SELECT dt.id, u.username, dt.amount 
            FROM dev_transactions dt 
            JOIN users u ON dt.target_user_id = u.id 
            WHERE dt.dev_user_id = :dev_id
        """)
        transactions = db.session.execute(transactions_query, {'dev_id': user_info[0]}).fetchall()

    if request.method == 'POST':
        
        if request.form.get("load_money"):
            if not is_dev:
                flash("You are not a developer.", "error")
                return redirect(url_for('user_page'))

            target_username = request.form.get("target_username")
            amount = request.form.get("amount")
            dev_password_input = request.form.get("dev_code")
            hashed_input_dev_code = MD5.new(dev_password_input.encode()).hexdigest()

            dev_password_check = db.session.execute(
                text("SELECT * FROM users WHERE username = :name and dev_password = :dev_code"),
                {'name': session["username"], 'dev_code': hashed_input_dev_code}
            ).fetchone()

            if dev_password_check:
                target_user = db.session.execute(text("SELECT * FROM users WHERE username = :username"), {'username': target_username}).fetchone()
                if target_user:
                    existing_transaction = db.session.execute(
                        text("SELECT id FROM dev_transactions WHERE dev_user_id = :dev_id AND target_user_id = :target_id"),
                        {'dev_id': user_info[0], 'target_id': target_user[0]}
                    ).fetchone()

                    if existing_transaction:
                        flash("You have already loaded money for this user. To load again, please revert the existing transaction first.", "error")
                        return redirect(url_for('user_page'))
                    if target_user[1] == session["username"]: 
                        flash("Error: Developers cannot load money into their own accounts.", "error")
                        return redirect(url_for('user_page'))
                    if int(amount) > 0:
                            flash(f"The amount of cant be negtive", "error")
                            return redirect(url_for('user_page'))

                    if int(amount) <= 15000000:
                     
                            time.sleep(1.5)
                            db.session.execute(text("UPDATE users SET money = money + :amount WHERE username = :username"), {'amount': int(amount), 'username': target_username})
                            
                            db.session.execute(
                                text("INSERT INTO dev_transactions (dev_user_id, target_user_id, amount) VALUES (:dev_id, :target_id, :amount)"),
                                {'dev_id': user_info[0], 'target_id': target_user[0], 'amount': int(amount)}
                            )
                            db.session.commit()
                            
                            flash(f"The amount of ${amount} was successfully transferred to user {target_user[1]}.", "success")
                            return redirect(url_for('user_page'))

                    else:
                        flash("Amount can't be more than 200.", "error")
                        return redirect(url_for('user_page'))
                else:
                    flash("User not found.", "error")
                    return redirect(url_for('user_page'))
            else:
                flash("Incorrect dev code. If you have forgotten your developer code, please contact the admin to reset it.", "error")
                return redirect(url_for('user_page'))
        
        elif request.form.get("revert_transaction"):
            if not is_dev:
                flash("You are not a developer.", "error")
                return redirect(url_for('user_page'))
                
            transaction_id = request.form.get("transaction_id")
            
            transaction_details = db.session.execute(
                text("SELECT * FROM dev_transactions WHERE id = :t_id AND dev_user_id = :d_id"),
                {'t_id': transaction_id, 'd_id': user_info[0]}
            ).fetchone()

            if transaction_details:
                target_user_id = transaction_details[2]
                amount_to_revert = transaction_details[3]

                db.session.execute(
                    text("UPDATE users SET money = GREATEST(0, money - :amount) WHERE id = :user_id"),
                    {'amount': amount_to_revert, 'user_id': target_user_id}
                )
                db.session.execute(
                    text("DELETE FROM dev_transactions WHERE id = :t_id"),
                    {'t_id': transaction_id}
                )
                db.session.commit()
                flash("Transaction successfully reverted.", "success")
                return redirect(url_for('user_page'))
            else:
                flash("Transaction not found or you don't have permission to revert it.", "error")
                return redirect(url_for('user_page'))

        elif request.form.get("show_token"):
            if not is_dev:
                flash("You are not a developer.", "error")
                return redirect(url_for('user_page'))

            dev_password_input = request.form.get("dev_code")
            hashed_input_dev_code = MD5.new(dev_password_input.encode()).hexdigest()

            dev_user_check = db.session.execute(
                text("SELECT dev_password FROM users WHERE username = :name AND dev_password = :dev_code"),
                {'name': session["username"], 'dev_code': hashed_input_dev_code}
            ).fetchone()

            if dev_user_check:
                revealed_token = user_info[8]
                user_name_encoded = encode_to_base64(username)
                return render_template('user.html',
                                       user_name=user_info[1],
                                       user_id=user_info[0],
                                       security_question=user_info[3],
                                       user_cash=user_info[5], 
                                       user_name_encoded=user_name_encoded,
                                       is_dev=is_dev,
                                       revealed_dev_token=revealed_token, 
                                       owns_quantum_computer=user_owns_quantum,
                                       transactions=transactions)
            else:
                flash("Incorrect dev code. If you have forgotten your developer code, please contact the admin to reset it.", "error")
                return redirect(url_for('user_page'))

        elif request.form.get("change_password"):
            current_password = request.form.get('current_password')
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")
            uid_from_form = request.form.get("uid")

            if not all([current_password, new_password, confirm_password, uid_from_form]):
                flash("All password fields are required.", "error")
                return redirect(url_for('user_page'))
            
            target_username = decode_from_base64(uid_from_form)
            
            if not target_username:
                flash("Invalid UID format.", "error")
                return redirect(url_for('user_page'))

            db_password_query = "SELECT password FROM users WHERE username = :username"
            db_password = db.session.execute(text(db_password_query), {'username': username}).fetchone()

            if db_password and MD5.new(current_password.encode()).hexdigest() == db_password[0]:
                if new_password == confirm_password:
                    hashed_new_password = MD5.new(new_password.encode()).hexdigest()
                    
                    db_query = "UPDATE users SET password = :password WHERE username = :username"
                    db.session.execute(text(db_query), {'password': hashed_new_password, 'username': target_username})
                    db.session.commit()

                    flash(f"Password has reset successfully.", "success")
                    return redirect(url_for('user_page'))
                else:
                    flash("New passwords do not match.", "error")
            else:
                flash("Current password does not match.", "error")
            
            return redirect(url_for('user_page'))

    user_name_encoded = encode_to_base64(username)
    return render_template('user.html',
                           user_name=user_info[1],
                           user_id=user_info[0],
                           security_question=user_info[3],
                           user_cash=user_info[5], 
                           user_name_encoded=user_name_encoded,
                           is_dev=is_dev,
                           revealed_dev_token=None, 
                           owns_quantum_computer=user_owns_quantum,
                           transactions=transactions)





@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        session.clear() 
        flash("You have logged out!", "info")
        return redirect(url_for('login_page'))

    elif 'admin_name' in session:
        session.clear() 
        flash("ADMIN has logged out!", "info")
        return redirect(url_for('login_page'))
        
    else:
        return redirect(url_for('login_page'))



@app.route('/products',methods=['GET', 'POST'])
def products_page():
    user_info = None
    category_options = ["Computer","Game","Software","Peripheral","All"]
    catagory = request.args.get('category')
    #הספגטי הכי מסריח שיש בעולם 
    if "username"  in session:
        user_info_query = "SELECT * FROM users WHERE username = :username"
        user_info = db.session.execute(text(user_info_query), {'username': session['username']}).fetchone()
        #INJCTION
        if catagory not in category_options or catagory == category_options[4]:
            #INJCTION
            items = db.session.execute(text("SELECT * FROM products where hidden = 0")).fetchall()
            return render_template('products.html', products=items,catagory=category_options[4],user_cash="You have: " + str(user_info[5])+ "$")
        else:
            #INJCTION
            items_query = "SELECT * FROM products WHERE category = :category AND hidden = 0"
            items = db.session.execute(text(items_query), {'category': catagory}).fetchall()
            return render_template('products.html', products=items,catagory=catagory,user_cash="You have: " + str(user_info[5])+ "$")
    else:
        if catagory not in category_options or catagory == category_options[4]:
            #INJCTION
            items = db.session.execute(text("SELECT * FROM products where hidden = 0")).fetchall()
            return render_template('products.html', products=items,catagory=category_options[4])
        else:
            #INJCTION
            items_query = "SELECT * FROM products WHERE category = :category AND hidden = 0"
            items = db.session.execute(text(items_query), {'category': catagory}).fetchall()
            return render_template('products.html', products=items,catagory=catagory)




@app.route('/product', methods=['GET', 'POST'])
def product():
    product_id = request.args.get('id')
    if not product_id:
        return "Product ID not provided", 400

    if request.method == 'POST':
        if 'username' not in session and 'admin_name' not in session:
            return "you are not authorized user, please <a href='/login'>login</a>",401


        if 'stockapi' in request.form:
            if 'admin_name' in session:
                return "Admins cannot add items to a cart.", 403
            
            url = request.form.get("stockapi")
            try:
                response = requests.get(url, timeout=5)

                if "item is in stock" in response.text:
                    user_info = db.session.execute(text("SELECT id FROM users WHERE username = :username"), {'username': session['username']}).fetchone()
                    userid = user_info[0]
                    
                    cart_item_query = text("SELECT * FROM cart_items WHERE user_id = :user_id AND product_id = :product_id")
                    if db.session.execute(cart_item_query, {'user_id': userid, 'product_id': product_id}).fetchone() is None:
                        insert_cart_query = text("INSERT INTO cart_items (user_id, product_id) VALUES (:user_id, :product_id)")
                        db.session.execute(insert_cart_query, {'user_id': userid, 'product_id': product_id})
                        db.session.commit()
                    
                    return "in_stock"
                
                elif "item is out of stock" in response.text:
                    return "out_of_stock"
                else:
                    return response.text, response.status_code

            except requests.RequestException:
                return "Error: Could not reach the stock service", 500


        elif 'comment_text' in request.form:
            if "admin_name" in session:
                 return "you need to be normal user do that!"
            user_info = db.session.execute(text("SELECT id FROM users WHERE username = :username"), {'username': session.get('username', '')}).fetchone()
            if not user_info:
                return "User not found", 404
            
            userid = user_info[0]
            comment_text = request.form.get("comment_text")
            
            insert_query = text("INSERT INTO comments (user_id, product_id, comment_text) VALUES (:user_id, :product_id, :comment_text)")
            db.session.execute(insert_query, {'user_id': userid, 'product_id': product_id, 'comment_text': comment_text})
            db.session.commit()
            
            return redirect(url_for('product', id=product_id))


        elif 'delete_comment_id' in request.form:
            comment_id_to_delete = request.form.get('delete_comment_id')
            comment_author = db.session.execute(text("SELECT user_id FROM comments WHERE id = :id"), {'id': comment_id_to_delete}).fetchone()
            if not comment_author:
                return "Comment not found", 404

            can_delete = False
     
            if 'admin_name' in session:
                can_delete = True

            elif 'username' in session:
                user_info = db.session.execute(text("SELECT id FROM users WHERE username = :username"), {'username': session['username']}).fetchone()
                if user_info and user_info[0] == comment_author[0]:
                    can_delete = True
            
            if can_delete:
                db.session.execute(text("DELETE FROM comments WHERE id = :id"), {'id': comment_id_to_delete})
                db.session.commit()
            else:
                return "You do not have permission to delete this comment.", 403
                
            return redirect(url_for('product', id=product_id))


    product_info = db.session.execute(text("SELECT * FROM products WHERE id = :id AND hidden = 0"), {'id': product_id}).fetchone()
    if not product_info:
        return "Product not found", 404

    comments_query = text("""
        SELECT c.id, c.comment_text, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.product_id = :product_id
    """)
    comments = db.session.execute(comments_query, {'product_id': product_id}).fetchall()
    
    is_admin = 'admin_name' in session
    
    return render_template(
        'product.html', 
        product=product_info, 
        comments=comments, 
        session_username=session.get('username'),
        is_admin_session=is_admin
    )



# היעילית פה חרא חייב דחוף לסדר את זה על כל מוצר יש שלוש קריאות למסד נתונים
#יש פה באג שעושים את הטריק הזה משלב 2 על המחשב הקוונטי אין לי מושג מה הבאג אבל יש באג והוא גורם לקריסה
@app.route('/cart', methods=['POST', "GET"])
def cart():
    if "admin_name" in session:
        return "you need to be normal user do that!"
    if "username" in session:
        user_info_query = "SELECT * FROM users WHERE username = :username"
        user_info = db.session.execute(text(user_info_query), {'username': session['username']}).fetchone()
        userid = user_info[0]

        cart_items_query = "SELECT * FROM cart_items WHERE user_id = :userid"
        cart_items_records = db.session.execute(text(cart_items_query), {'userid': userid}).fetchall()
        items_for_template = []
        total_price = 0
        for item in cart_items_records:
            product_id = item[2]
            product_query = "SELECT * FROM products WHERE id = :product_id"
            #INJCTION
            P = db.session.execute(text(product_query), {'product_id': product_id}).fetchone()
            #INJCTION
            product_details = db.session.execute(text(product_query), {'product_id': product_id}).fetchone()
            #INJCTION
            quantity_query = "SELECT * from cart_items WHERE user_id = :userid AND product_id = :product_id"
            quntity = db.session.execute(text(quantity_query), {'userid': userid, 'product_id': product_id}).fetchone()
            product_data = {
                "id": product_details[0],
                "name": product_details[1],
                "price": product_details[3],
                "image_url": product_details[4],
                "quantity": quntity[3]
            }
            total_price = total_price + P[3] * quntity[3]
            items_for_template.append(product_data)

        if request.method == "POST" and request.form.get("remove_item"):
            item_id_to_remove = request.form.get("remove_item")
            print(f"remove item: {item_id_to_remove}")
            delete_query = "DELETE FROM cart_items WHERE user_id = :userid AND product_id = :product_id"
            db.session.execute(
                #INJCTION
                text(delete_query), {'userid': userid, 'product_id': item_id_to_remove}
            )
            db.session.commit()
 
            item_query = "SELECT * FROM products WHERE id = :id"
            item = db.session.execute(
                #INJCTION
                text(item_query), {'id': item_id_to_remove}
            ).fetchone()
            db.session.commit()
            return  redirect(f"/cart")
        
        if request.method == "POST" and "productid_increase" in request.form:
            update_query = "UPDATE cart_items SET quantity = quantity + :quantity WHERE user_id = :userid AND product_id = :product_id"
            db.session.execute(
                #INJCTION
                text(update_query), {'quantity': request.form.get("quantity"), 'userid': userid, 'product_id': request.form['productid_increase']}
            )
            db.session.commit()
            return  redirect(f"/cart")
        if request.method == "POST" and "productid_dcrease" in request.form:
            update_query = "UPDATE cart_items SET quantity = quantity - :quantity WHERE user_id = :userid AND product_id = :product_id"
            db.session.execute(
                #INJCTION
                text(update_query), {'quantity': request.form.get("quantity"), 'userid': userid, 'product_id': request.form['productid_dcrease']}
            )
            
            select_quantity_query = "SELECT quantity FROM cart_items WHERE user_id = :userid AND product_id = :product_id"
            if db.session.execute(
                #INJCTION
                text(select_quantity_query), {'userid': userid, 'product_id': request.form['productid_dcrease']}
            ).fetchone()[0] == 0:
                delete_query = "DELETE FROM cart_items WHERE user_id = :userid AND product_id = :product_id"
                db.session.execute(
                    #INJCTION
                    text(delete_query), {'userid': userid, 'product_id': request.form['productid_dcrease']}
                )
            db.session.commit()
            return  redirect(f"/cart")
            # user_cash = user_info[5]
            # if total_price > user_cash:
            #     message = {
            #         "text": "you dont have engthe monnay",
            #         "color": "red"
            #     }
            #     return render_template("cart.html",
            #                            cart_items=items_for_template,
            #                            grand_total=total_price,
            #                            user_name=user_info[1],
            #                            user_cash=user_info[5],
            #                            message=message)

        return render_template("cart.html",
                               cart_items=items_for_template,
                               grand_total=total_price,
                               user_name=user_info[1],
                               user_cash=user_info[5])

    else:
        return "you are not authorized user, please <a href='/login'>login</a>", 401

    
@app.route('/cart/checkout', methods=['POST', 'GET'])
def chackout():
    if "admin_name" in session:
        return "you need to be normal user do that!"

    if "username" in session:
        user_info_query = "SELECT * FROM users WHERE username = :username"
        user_info = db.session.execute(text(user_info_query), {'username': session['username']}).fetchone()
        userid = user_info[0]
        user_cash = user_info[5]
        
        cart_items_query = "SELECT * FROM cart_items WHERE user_id = :userid"
        cart_items_records = db.session.execute(text(cart_items_query), {'userid': userid}).fetchall()
        
        if not cart_items_records:
            return redirect(url_for('cart'))
        
        total_price = 0
        Sorder_id = 0
        products_data_in_cart = []

        for item in cart_items_records:
            product_query = "SELECT * FROM products WHERE id = :product_id"
            P = db.session.execute(text(product_query), {'product_id': item[2]}).fetchone()
            if P:
                products_data_in_cart.append({'details': P, 'quantity': item[3]})
                
                if P[0] == 99:
                    Sorder_id = 99
                elif P[0] == 2 and Sorder_id != 99:
                    Sorder_id = 2
                
                total_price += P[3] * item[3]

        if total_price > user_cash:
            flash("you dont have enough monnay", "info")
            return redirect(url_for('cart'))
        elif total_price <= 0:
            flash("total cant be 0 or less", "info")
            return redirect(url_for('cart'))
        fun_fact = ""
        order_id = ""
        if Sorder_id != 2 and Sorder_id != 99:
            string_to_hash = ""
            for item in cart_items_records:
                string_to_hash += str(item[2])
            order_id = MD5.new(string_to_hash.encode()).hexdigest()

            with open("fun facts.txt", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                random_line = random.choice(lines)
                fun_fact = random_line

        elif Sorder_id == 2:
            order_id = "amiga500"
            fun_fact = "the entire shopping system for this website was developed by the user customer35 on the amiga 500. Isn't that cool?"
            order_id = MD5.new(order_id.encode()).hexdigest()
        elif Sorder_id == 99:
            order_id = "qun_computer"
            db.session.execute(text("UPDATE users SET does_own_qun = 1 WHERE id = :id"), {'id': userid})
            order_id = MD5.new(order_id.encode()).hexdigest()
        



        user_cash = user_cash - total_price
        update_user_query = "UPDATE users SET money = :money WHERE id = :id"
        db.session.execute(text(update_user_query), {'money': user_cash, 'id': userid})
        
        delete_cart_query = "DELETE FROM cart_items WHERE user_id = :userid"
        db.session.execute(text(delete_cart_query), {'userid': userid})
        db.session.commit()

        items_for_template = []
        for saved_item in products_data_in_cart:
            product_details = saved_item['details']
            product_data = {
                "id": product_details[0],
                "name": product_details[1],
                "price": product_details[3],
                "image_url": product_details[4],
                "quantity": saved_item['quantity']
            }
            items_for_template.append(product_data)
        return render_template("checkout.html",
                               total=total_price,
                               user_name=user_info[1],
                               user_cash=user_info[5], 
                               order_id=order_id, 
                               ordered_items=items_for_template,fan_fact=fun_fact)
    else:
        return "you are not authorized user, please <a href='/login'>login</a>", 401

@app.route('/Adm1n_l091n', methods=['POST', 'GET'])
def admin():
    if 'admin_lockout_time' in session and datetime.now(timezone.utc) < session['admin_lockout_time']:
        remaining_seconds = (session['admin_lockout_time'] - datetime.now(timezone.utc)).seconds
        message = {
            "text": f"Too many failed attempts. Please try again in {remaining_seconds} seconds.",
            "color": "red"
        }
        return render_template('admin_login.html', message=message), 429

    if request.method == "POST":
        username = request.form.get('adminname')
        password = request.form.get('password')   
        
        query_string = "SELECT * FROM admins WHERE name = :username AND password = :password"
        result = db.session.execute(text(query_string), {'username': username, 'password': password}).fetchone()
        
        if result:
            session.pop('admin_login_attempts', None)
            session.pop('admin_lockout_time', None)
            
            session.clear()
            session['admin_name'] = username 
            return redirect(url_for('admin_panal'))
        else:
            session['admin_login_attempts'] = session.get('admin_login_attempts', 0) + 1
            
            if session['admin_login_attempts'] >= 5:
                session['admin_lockout_time'] = datetime.now(timezone.utc) + timedelta(minutes=1)
                session.pop('admin_login_attempts', None)
                message = {
                    "text": "Too many failed attempts. You have been locked out for 1 minute.",
                    "color": "red"
                }
                return render_template('admin_login.html', message=message), 429

            message = {
                "text": "Invalid username or password.",
                "color": "red"
            }
            return render_template('admin_login.html', message=message), 401
            
    return render_template('admin_login.html')

@app.route('/admin/delete_comment', methods=['GET'])
def admin_delete_comment():
    comment_id = request.args.get('id')
    
    if "admin_name" not in session:
        return "unauthorized", 401
    if not comment_id:
        return "Bad Request: Comment ID is missing", 400

    author_query = text("""
        SELECT u.username 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.id = :comment_id
    """)
    author_result = db.session.execute(author_query, {'comment_id': comment_id}).fetchone()

    if author_result is None:
        return "Comment not found", 404

    author_username = author_result[0]

    delete_query = text("DELETE FROM comments WHERE id = :comment_id")
    db.session.execute(delete_query, {'comment_id': comment_id})
    db.session.commit()
    
    return f"Comment by {author_username} was successfully deleted."
@app.route('/admin_panal', methods=['POST', 'GET'])
def admin_panal():
    if 'admin_name' not in session:
       return "Unauthorized", 401
    
    if request.method == "POST":
        action = request.form.get('action')

        if action == 'reset_dev_code':
            dev_username_to_update = request.form.get('dev_username')
            new_dev_code = request.form.get('new_dev_code')
            if dev_username_to_update and new_dev_code:
                find_dev_query = text("SELECT id FROM users WHERE is_dev = 1 AND username = :username")
                dev_user = db.session.execute(find_dev_query, {'username': dev_username_to_update}).fetchone()
                if dev_user:
                    hashed_code = MD5.new(new_dev_code.encode()).hexdigest()
                    update_query = text("UPDATE users SET dev_password = :dev_password WHERE username = :username")
                    db.session.execute(update_query, {'dev_password': hashed_code, 'username': dev_username_to_update})
                    db.session.commit()
                    flash(f"Dev code for {dev_username_to_update} was updated successfully!", 'success')
                else:
                    flash(f"User {dev_username_to_update} is not a developer.", 'error')

        elif action == 'edit_product_description':
            product_id_to_edit = request.form.get('product_id')
            new_description = request.form.get('new_description')
            if product_id_to_edit and new_description is not None:
                update_query = text("UPDATE products SET description = :description WHERE id = :id")
                db.session.execute(update_query, {'description': new_description, 'id': product_id_to_edit})
                db.session.commit()
                flash(f"Description for product ID {product_id_to_edit} has been updated.", 'success')
        
        return redirect(url_for('admin_panal'))

    admin_username = session['admin_name']
    
    all_users = db.session.execute(text("SELECT id, username, money, is_dev FROM users ORDER BY id")).fetchall()
    
    all_products = db.session.execute(text("SELECT * FROM products WHERE id != 99 ORDER BY id")).fetchall()
    
    developers = db.session.execute(text("SELECT id, username FROM users WHERE is_dev = 1")).fetchall()
        
    return render_template('admin_panal.html', 
                           admin_name=admin_username,
                           users=all_users,
                           products=all_products,
                           developers=developers)






@app.route('/quantum_panel', methods=['GET', 'POST'])
def quantum_panel():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    user_owns_quantum = db.session.execute(
        text("SELECT does_own_qun FROM users WHERE username = :username"), 
        {'username': session['username']}
    ).scalar()
    
    if not user_owns_quantum:
        flash("Access Denied.", "error")
        return redirect(url_for('user_page'))

    output = "Awaiting command..."
    if request.method == 'POST':
        ip_address = request.form.get('ip_address')

        
        if ip_address:

            command = f"ping -c 4 {ip_address}"
            try:

                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                output = e.output 
        
    return render_template('quantum_panel.html', output=output)


if __name__ == "__main__":
    app.run(debug=False, port=8080,host="0.0.0.0")
