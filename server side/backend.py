from flask import Flask, render_template,request, redirect, url_for, session,  flash,request,jsonify , Response,make_response, send_from_directory

import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import os



app = Flask(__name__)

app.secret_key = "super-secret-key"

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://retro_user:1234@db/app'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://retro_user:1234@10.0.0.21:3306/app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, ''), 'robots.txt')


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
            write_log("user: "+ username + " has logged in")
            response = make_response('Login successful', 200)

            response.headers['X-User-ID'] = result.id
            response.headers['X-Redirect-Url'] = url_for('user_page')
            
            return response
        else:
            return 'Invalid username or password', 401

@app.route('/reset',methods=['POST',"GET"])
def reset():
    if request.method == 'POST':
        username = request.form.get('username')
        if 'new_password' in request.form and session.get('can_reset_password'):
            
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
         
            # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
            if new_password == confirm_password:
                hashed_new_password = MD5.new(new_password.encode()).hexdigest()
                db_query = "UPDATE users SET password = :password WHERE username = :username"
                #INJCTION
                db.session.execute(text(db_query), {'password': hashed_new_password, 'username': username})
                db.session.commit()
                write_log("user: " + username + " has reset his password")
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
                write_log(message="user:" + username + " reset password")
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
        user_info_query = "SELECT * FROM users WHERE username = :username"
        user_info = db.session.execute(text(user_info_query), {'username': username}).fetchone()
        if request.method == 'POST':
                current_password = request.form.get('current_password')
                new_password = request.form.get("new_password")
                confirm_password = request.form.get("confirm_password")
                
                if request.form.get("uid"):
                    user_name = request.form.get("uid")
                    current_user = caesar_cipher(user_name,-5)
                    print(current_user)
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
                        write_log("user: " + username + " has reset his password")

                        flash("Password reset successfully","info")
                        return redirect(url_for('user_page'))
                        #return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
                    else:

                        flash("Passwords do not match","error")
                        return redirect(url_for('user_page'))
                    #return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
                else:
                        flash("current password not match","error")
                        return redirect(url_for('user_page'))
                        #return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
       
        return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5))
    else:
        return "you are not authorized user, please <a href='/login'>login</a>",401




@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        session.clear()
        write_log(f"User '{username}' has logged out")
        flash("You have logged out!", "info")
        return redirect(url_for('login_page'))

    elif 'admin_name' in session:
        session.clear() 
        write_log("ADMIN has logged out")
        flash("ADMIN has logged out!", "info")
        return redirect(url_for('login_page'))
        
    else:
        
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

        order_id = ""
        if Sorder_id != 2 and Sorder_id != 99:
            string_to_hash = ""
            for item in cart_items_records:
                string_to_hash += str(item[2])
            order_id = MD5.new(string_to_hash.encode()).hexdigest()
        elif Sorder_id == 2:
            order_id = "amiga500"
            order_id = MD5.new(order_id.encode()).hexdigest()
        elif Sorder_id == 99:
            order_id = "qun_computer"
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
        write_log("user: "+ session['username'] + " checkout")
        return render_template("checkout.html",
                               total=total_price,
                               user_name=user_info[1],
                               user_cash=user_info[5], 
                               order_id=order_id, 
                               ordered_items=items_for_template)
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
            write_log("ADMIN has logged in")
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
    
    # כתוב ללוג
    write_log(f"ADMIN has deleted {author_username}'s comment")
    
    return f"Comment by {author_username} was successfully deleted."

@app.route('/admin_panal', methods=['POST', 'GET'])
def admin_panal():
    if 'admin_name' not in session:
       return "Unauthorized",401
    
    admin_username = session['admin_name']
    admin_info_query = text("SELECT * FROM admins WHERE name = :name")
    admin_info = db.session.execute(admin_info_query, {"name": admin_username}).fetchone()

    file_path = '/var/logs/'
    file_name = 'log.txt'
    log_content = "log"
    if request.method == "POST":
        file_name = request.form.get('fp')
        if 'fp' in request.form:
            try:
                with open(file_path + file_name, 'r') as file:
                    log_content = file.read()
                    return render_template('admin_panal.html', 
                           admin_name=admin_info[1], 
                           log_content=log_content)
                        
            except Exception as e:
                log_content = "Error",e
                flash(f"ERORR", 'error')


        if 'addUser' in request.form:
            username = request.form.get('addUser')
            if username:
                user_exists_query = text("SELECT * FROM users WHERE username = :username")
                user_exists = db.session.execute(user_exists_query, {"username": username}).fetchone()

                if user_exists:
                    update_query = text("UPDATE users SET internal = TRUE WHERE username = :username")
                    db.session.execute(update_query, {"username": username})
                    db.session.commit()
                    flash(f"User '{username}' has been updated to internal.", 'success')
                else:
                    flash(f"User '{username}' was not found.", 'error')

    return render_template('admin_panal.html', 
                           admin_name=admin_info[1], 
                           log_content=log_content)

def write_log(message):
    with open('/var/logs/log.txt', 'a') as log_file:
        log_file.write("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"+ '\n')
        log_file.write(message + '\n')

if __name__ == "__main__":
    app.run(debug=True, port=5000,host="0.0.0.0")