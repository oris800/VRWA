from flask import Flask, render_template,request, redirect, url_for, session,  flash,request,jsonify , Response,make_response, send_from_directory
import random 
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import os
import time
import contextlib
import traceback
import io


app = Flask(__name__)

app.secret_key = "super-secret-key"

db_user = os.getenv('DB_USER', 'retro_user')
db_password = os.getenv('DB_PASSWORD', '1234')
db_host = os.getenv('DB_HOST', 'localhost') #
db_name = os.getenv('DB_NAME', 'app')
db_port = 3306 

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




def caesar_cipher(text, shift):
    """
    Encrypts or decrypts text using the Caesar cipher method.
    A positive shift encrypts, a negative shift decrypts.
    """
    result = ""
    for char in text:
        if 'a' <= char <= 'z':
            shifted_char = chr(((ord(char) - ord('a') + shift) % 26) + ord('a'))
            result += shifted_char
        elif 'A' <= char <= 'Z':
            shifted_char = chr(((ord(char) - ord('A') + shift) % 26) + ord('A'))
            result += shifted_char
        else:
            result += char 
    return result

# ... כאן מתחילה הפונקציה user_page ...

@app.route('/robots.txt')
def robots_txt():

    try:
        return send_from_directory(app.root_path, 'robots.txt')
    except FileNotFoundError:

        return "File not found", 404

@app.route('/')
def home():
    products = db.session.execute(text("SELECT * FROM products WHERE show_on_page = 1")).fetchall()    
    if "username" in session:
        return render_template('index.html', username=session["username"], products=products)
    else:
        return render_template('index.html', products=products)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    # POST request from JavaScript
    if request.method == 'POST':
        # הפעם הנתונים מגיעים כ-form-data, לא JSON
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
            # 3. בכישלון, החזר תשובת שגיאה עם טקסט
            return 'Invalid username or password', 401

#חשובבבבב יש םה באג של עקיפת מנגנון אימות קריטיק אחושרמוטה
@app.route('/reset',methods=['POST',"GET"])
def reset():
    if request.method == 'POST':
        username = request.form.get('username')
        if 'new_password' in request.form and session.get('can_reset_password'): #לא מובן לי המכינקה שמונעת עקיםת שלבים לחקור בהמשך
            
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
         
            # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
            if new_password == confirm_password:
                hashed_new_password = MD5.new(new_password.encode()).hexdigest()
                db_query = "UPDATE users SET password = :password WHERE username = :username"
                #INJCTION
                db.session.execute(text(db_query), {'password': hashed_new_password, 'username': username})
                db.session.commit()
                session.pop('can_reset_password', None)

                flash("Password has been reset successfully!")
                return redirect(url_for('login_page'))
            else:
                message = {
                    "text": "Passwords do not match",
                    "color": "red"
                }
                return render_template('reset.html',message=message,allow_password_reset=True,username=username)

        
        elif 'security_answer' in request.form:
            submitted_answer = request.form.get('security_answer')            
            db_quary = "SELECT security_answer FROM users WHERE username = :username"
            #INJCTION
            result2 = db.session.execute(text(db_quary), {'username': username}).fetchone()
            
            if result2 and submitted_answer == result2[0]:
                
                session['can_reset_password'] = True
                
                message = {
                "text": "Security answer is currect.",
                "color": "green"
                }
                return render_template('reset.html',message=message,allow_password_reset=True,username=username)
            else:  
                message = {
                "text": "Security answer is worng.",
                "color": "red"
                }
                db_quary = "SELECT security_question FROM users WHERE username = :username"
                #INJCTION
                result = db.session.execute(text(db_quary), {'username': username}).fetchone()
                return render_template('reset.html',username=username ,security_question=result[0],message=message)

        elif 'username' in request.form:

    
            db_quary = "SELECT security_question FROM users WHERE username = :username"
            result = db.session.execute(text(db_quary), {'username': username}).fetchone()


            if result:
                return render_template('reset.html',username=username ,security_question=result[0])
            else:
             message = {
                "text": "the user not found",
                "color": "red"
            }
        

            return render_template('reset.html', message=message)

    return render_template('reset.html')



# שנה את methods ל-POST כדי שהפונקציה תוכל לקבל נתונים
@app.route('/login/chack', methods=['POST'])
def chack_user():
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
        return "internal Error", 500



@app.route('/user',methods=['GET', 'POST'])
def user_page():
    if "admin_name" in session:
        return redirect(url_for('admin_panal'))
    if "username" in session:
        username = session["username"]  
        user_owns_quantum = db.session.execute(text("SELECT does_own_qun FROM users WHERE username = :username"), {'username': username}).scalar()
        is_dev = False
        username = session["username"]  
        user_info_query = "SELECT * FROM users WHERE username = :username"
        user_info = db.session.execute(text(user_info_query), {'username': username}).fetchone()
        if user_info[7] == True:
            is_dev = True
        else:
            is_dev = False

        if request.method == 'POST':
            
            if request.form.get("load_money"):
                target_username = request.form.get("target_username")
                amount = request.form.get("amount")
                dev_password_input = request.form.get("dev_code")
                hashed_input_dev_code = MD5.new(dev_password_input.encode()).hexdigest()

                dev_password = db.session.execute(
                text("SELECT * FROM users WHERE username = :name and dev_password = :dev_code"),
                {
                    'name': session["username"],
                    'dev_code': hashed_input_dev_code
                }
                ).fetchone()

                if dev_password:
                    dose_user_exits = db.session.execute(text("SELECT * FROM users WHERE username = :username"), {'username': target_username}).fetchone()
                    if dose_user_exits:

                        current_balance_query = text("SELECT money FROM users WHERE username = :username")
                        current_balance = db.session.execute(current_balance_query, {'username': target_username}).fetchone()[0]

                        if int(amount) <= 200:
                            if current_balance + int(amount) <= 400:

                                time.sleep(1.5)

                                db.session.execute(text("UPDATE users SET money = money + :amount WHERE username = :username"), {'amount': int(amount), 'username': target_username})
                                db.session.commit()
                                
                                flash(f"The amount of ${amount} was successfully transferred to user {dose_user_exits[1]}.", "success")
                                return redirect(url_for('user_page'))
                            else:
                                flash("This transaction would exceed the user's total balance limit of $400.", "error")
                                return redirect(url_for('user_page'))
                        else:
                            flash("amount cant be more than 200", "error")
                            return redirect(url_for('user_page'))
                    else:
                        flash("user not found", "error")
                        return redirect(url_for('user_page'))
                else:
                    flash("Incorrect dev code. If you have forgotten your developer code, please contact the admin and ask him to reset your dev code from his admin panel.", "error")
                    return redirect(url_for('user_page'))
            
            elif request.form.get("show_token"):
                dev_password_input = request.form.get("dev_code")
                hashed_input_dev_code = MD5.new(dev_password_input.encode()).hexdigest()

                dev_user_check = db.session.execute(
                    text("SELECT dev_password FROM users WHERE username = :name AND dev_password = :dev_code"),
                    {'name': session["username"], 'dev_code': hashed_input_dev_code}
                ).fetchone()

                if dev_user_check:
                    revealed_token = user_info[8]
                    return render_template('user.html',
                                           user_name=user_info[1],
                                           user_id=user_info[0],
                                           security_question=user_info[3],
                                           user_cash=user_info[5], 
                                           user_name_encoded=caesar_cipher(username,5),
                                           is_dev=is_dev,
                                           revealed_dev_token=revealed_token, owns_quantum_computer=user_owns_quantum)
                else:
                    flash("Incorrect dev code. If you have forgotten your developer code, please contact the admin and ask him to reset your dev code from his admin panel.", "error")
                    return redirect(url_for('user_page'))

            elif request.form.get("change_password"):
                
                current_password = request.form.get('current_password')
                new_password = request.form.get("new_password")
                confirm_password = request.form.get("confirm_password")
                
                if request.form.get("uid"):
                    user_name = request.form.get("uid")
                    current_user = caesar_cipher(user_name,-5)
                else:
                    return "Error uid missing "
    
                db_password_quray = "SELECT password FROM users WHERE username = :username"
                db_password =  db.session.execute(text(db_password_quray), {'username': username}).fetchone()
                if MD5.new(current_password .encode()).hexdigest() == db_password[0]:
                    if new_password == confirm_password:
                        hashed_new_password = MD5.new(new_password.encode()).hexdigest()
                        db_query = "UPDATE users SET password = :password WHERE username = :username"
                        db.session.execute(text(db_query), {'password': hashed_new_password, 'username': current_user})
                        db.session.commit()
                        flash("Password reset successfully","success")
                        return redirect(url_for('user_page'))
                    else:
                        flash("Passwords do not match","error")
                        return redirect(url_for('user_page'))
                else:
                        flash("current password not match","error")
                        return redirect(url_for('user_page'))
        print(user_owns_quantum)

        return render_template('user.html',
                               user_name=user_info[1],
                               user_id=user_info[0],
                               security_question=user_info[3],
                               user_cash=user_info[5], 
                               user_name_encoded=caesar_cipher(username,5),
                               is_dev=is_dev,
                               revealed_dev_token=None, owns_quantum_computer=user_owns_quantum)
    else:
        return "you are not authorized user, please <a href='/login'>login</a>",401


@app.route('/logout')
def logout():
    # בדוק אם משתמש כלשהו (רגיל או אדמין) מחובר
    if 'username' in session:
        # שמור את שם המשתמש בצד לפני מחיקת הסשן
        username = session['username']
        session.clear() # נקה את הסשן
        flash("You have logged out!", "info")
        return redirect(url_for('login_page'))

    elif 'admin_name' in session:
        session.clear() # נקה את הסשן
        flash("ADMIN has logged out!", "info")
        return redirect(url_for('login_page'))
        
    else:
        # אם אף אחד לא מחובר, פשוט הפנה לדף הכניסה
        return redirect(url_for('login_page'))


# מוצרים מוצרים  מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים 

@app.route('/products',methods=['GET', 'POST'])
def products_page():
    user_info = None
    category_options = ["Computer","Game","Software","Peripheral","All"]
    catagory = request.args.get('category')
    #הספגטי הכי מסריח שיש בעולם סעמק
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
    if request.method == "POST":
        username = request.form.get('adminname')
        password = request.form.get('password')   
        
        hashed_input_password = MD5.new(password.encode()).hexdigest()
            
        query_string = "SELECT * FROM admins WHERE name = :username AND password = :password"
        result = db.session.execute(text(query_string), {'username': username, 'password': hashed_input_password}).fetchone()
        
        if result:
            session.clear()
            session['admin_name'] = username 
            return redirect(url_for('admin_panal'))
        else:
            return "Invalid username or password" 
            
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
    
    admin_username = session['admin_name']
    admin_info_query = text("SELECT * FROM admins WHERE name = :name")
    admin_info = db.session.execute(admin_info_query, {"name": admin_username}).fetchone()

    devs_from_db = db.session.execute(text("SELECT id, username FROM users WHERE is_dev = 1")).fetchall()
        
    if request.method == "POST":
        if 'change_password' in request.form:
            dev_username_to_update = request.form.get('dev_username')
            new_dev_code = request.form.get('new_dev_code')

            if dev_username_to_update and new_dev_code:
                find_dev_query = text("SELECT * FROM users WHERE is_dev = 1 AND username = :username")
                dose_user_dev = db.session.execute(find_dev_query, {'username': dev_username_to_update}).fetchone()
                
                if dose_user_dev:
                    hashed_password = MD5.new(new_dev_code.encode()).hexdigest()
                    
                    update_query = text("UPDATE users SET dev_password = :dev_password WHERE username = :username")
                    db.session.execute(update_query, {'dev_password': hashed_password, 'username': dev_username_to_update})
                    db.session.commit()
                    flash(f"dev code for {dev_username_to_update} was updated successfully!", 'success')
                else:
                    return "dev not found", 404


    return render_template('admin_panal.html', 
                           admin_name=admin_info[1],
                           developers=devs_from_db)


def create_sandbox():

    restricted_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "True": True,
            "False": False,
            "None": None
        }
    }
    return restricted_globals

@app.route('/quantum_control_panel')
def quantum_panel():
    if db.session.execute(text("SELECT does_own_qun FROM users WHERE username = :username"), {'username': session.get('username', '')}).fetchone()[0] != True:
        return "you need to buy the quantum computer first!", 403
    else:
        return render_template('quantum_control_panel.html', output="Awaiting command...")

@app.route('/quantum_run', methods=['POST'])
def quantum_run():
    if db.session.execute(text("SELECT does_own_qun FROM users WHERE username = :username"), {'username': session.get('username', '')}).fetchone()[0] != True:
        return "you need to buy the quantum computer first!", 403
    else:
        code = request.form.get('code', '')
        output_buffer = io.StringIO()

        final_output = "Execution finished with no output."

        try:
            sandbox_globals = create_sandbox()

            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                exec(code, sandbox_globals)
            

            result = output_buffer.getvalue()
            if result:
                final_output = result

        except Exception:

            final_output = "Execution Error: Invalid syntax or restricted operation."
            
    return render_template('quantum_control_panel.html', output=final_output)


if __name__ == "__main__":
    app.run(debug=True, port=8080,host="0.0.0.0")