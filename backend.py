from flask import Flask, render_template,request, redirect, url_for, session,  flash,request, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import os



app = Flask(__name__)

app.secret_key = "super-secret-key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://retro_user:1234@10.0.0.15/app'
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

@app.route('/')
def home():
    products = db.session.execute(text("SELECT * FROM products WHERE show_on_page = 1")).fetchall()    
    if "username" in session:

        #INJCTION
        return render_template('index.html', username=session["username"], products=products)
    else:
        return render_template('index.html', products=products)


@app.route('/login',methods=['GET', 'POST'])
def login_page():
    if request.method  == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')        
        hashed_input_password = MD5.new(password.encode()).hexdigest()
         # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
        query_string = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_input_password}'"
        #INJCTION
        query = text(query_string)
        result = db.session.execute(query).fetchone()

        if result: 
            session.clear() 
            session['username'] = username
            return redirect(url_for('user_page'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/reset',methods=['POST',"GET"])
def reset():
    if request.method == 'POST':
        username = request.form.get('username')
        if 'new_password' in request.form and session.get('can_reset_password'): #לא מובן לי המכינקה שמונעת עקיםת שלבים לחקור בהמשך
            
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
         
            # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
            if new_password == confirm_password:
                db_query = f"UPDATE users SET password = '{MD5.new(new_password.encode()).hexdigest()}' WHERE username = '{username}'"
                #INJCTION
                db.session.execute(text(db_query))
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
            print(submitted_answer)   
            db_quary = f"SELECT security_answer FROM users WHERE username = '{username}'"
            #INJCTION
            result2 = db.session.execute(text(db_quary)).fetchone()
            
            if submitted_answer == result2[0]:
                
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
                db_quary = f"SELECT security_question FROM users WHERE username = '{username}'"
                #INJCTION
                result = db.session.execute(text(db_quary)).fetchone()
                return render_template('reset.html',username=username ,security_question=result[0],message=message)

        elif 'username' in request.form:

    
            db_quary = f"SELECT security_question FROM users WHERE username = '{username}'"
            result = db.session.execute(text(db_quary)).fetchone()


            if result:
                return render_template('reset.html',username=username ,security_question=result[0])
            else:
             message = {
                "text": "the user not found",
                "color": "red"
            }
        

            return render_template('reset.html', message=message)

    return render_template('reset.html')        



@app.route('/user',methods=['GET', 'POST'])
def user_page():
    if "username" in session:
        username = session["username"]  
        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
        #INJCTION
        if request.method == 'POST':
                current_password = request.form.get('current_password')
                new_password = request.form.get("new_password")
                confirm_password = request.form.get("confirm_password")
                
                if request.form.get("uid"):
                #כאן מקבלים שם משתמש מוצפן
                    user_name = request.form.get("uid")
                    current_user = caesar_cipher(user_name,-5)
                    print(current_user)
                else:
                    return "Error uid missing "
    
                db_password_quray =f"SELECT password FROM users WHERE username = '{username}'"
                #INJCTION
                db_password =  db.session.execute(text(db_password_quray)).fetchone()
                if MD5.new(current_password .encode()).hexdigest() == db_password[0]:
                    if new_password == confirm_password:
                        db_query = f"UPDATE users SET password = '{MD5.new(new_password .encode()).hexdigest()}' WHERE username = '{current_user}'"
                        db.session.execute(text(db_query))
                        db.session.commit()
                        write_log("user: " + username + " reset password")

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
    session.clear()
    flash("you have log out!","info")
    return redirect(url_for('login_page')) 


# מוצרים מוצרים  מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים 

@app.route('/products',methods=['GET', 'POST'])
def products_page():
    user_info = None
    category_options = ["Computer","Game","Software","Peripheral","All"]
    catagory = request.args.get('category')
    #הספגטי הכי מסריח שיש בעולם סעמק
    if "username"  in session:
        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
        #INJCTION
        if catagory not in category_options or catagory == category_options[4]:
            #INJCTION
            items = db.session.execute(text("SELECT * FROM products where hidden = 0")).fetchall()
            return render_template('products.html', products=items,catagory=category_options[4],user_cash="You have: " + str(user_info[5])+ "$")
        else:
            #INJCTION
            items = db.session.execute(text(f"SELECT * FROM products WHERE category = '{catagory}' AND hidden = 0")).fetchall()
            return render_template('products.html', products=items,catagory=catagory,user_cash="You have: " + str(user_info[5])+ "$")
    else:
        if catagory not in category_options or catagory == category_options[4]:
            #INJCTION
            items = db.session.execute(text("SELECT * FROM products where hidden = 0")).fetchall()
            return render_template('products.html', products=items,catagory=category_options[4])
        else:
            #INJCTION
            items = db.session.execute(text(f"SELECT * FROM products WHERE category = '{catagory}' AND hidden = 0")).fetchall()
            return render_template('products.html', products=items,catagory=catagory)
#מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד 




@app.route('/product',methods=['GET', 'POST'])
def product():
    id = request.args.get('id')
    if id:
        comments = db.session.execute(text(f"SELECT * FROM comments WHERE product_id = '{id}'")).fetchall()
     
        comments_list = []
        for comment in comments:
            comment_id = comment[0]
            user_id = comment[2]
            comment_text = comment[3]

            username_result = db.session.execute(text(f"SELECT username FROM users where id = '{user_id}'")).fetchone()
            if username_result:
                username = username_result[0]

            comments_list.append([comment_id, comment_text, username])     

        product = db.session.execute(text(f"SELECT * FROM products WHERE id = '{id}'")).fetchone()

        if product and product[8] == 0:
            product_info = {
                "id": product[0],
                "name":product[1],
                "price":product[3],
                "release_date": product[2],
                "image_url": product[4],
                "description": product[5]
            }
        
            if request.method == "POST" and "comment_text" in request.form:
                if 'username' not in session:
                    return "you are not authorized user, please <a href='/login'>login</a>", 401
                
                user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
                userid = user_info[0]

                comment_text = request.form.get("comment_text")
                insert_query = f"INSERT INTO comments (user_id, product_id, comment_text) VALUES ({userid}, {id}, '{comment_text}')"
                db.session.execute(text(insert_query))
                db.session.commit()
                write_log("user: " + session['username'] + " post comment")
                return redirect(f"/product?id={product_info['id']}")

            if request.method == "POST" and 'delete_comment_id' in request.form:
                if 'username' not in session:
                    return "Not authorized", 401

                comment_id_to_delete = request.form.get('delete_comment_id')
                logged_in_user = db.session.execute(text(f"SELECT id FROM users WHERE username = '{session['username']}'")).fetchone()
                logged_in_user_id = logged_in_user[0]
                comment_author = db.session.execute(text(f"SELECT user_id FROM comments WHERE id = {comment_id_to_delete}")).fetchone()
                
                if comment_author and logged_in_user_id == comment_author[0]:
                    db.session.execute(text(f"DELETE FROM comments WHERE id = {comment_id_to_delete}"))
                    db.session.commit()
                    write_log("user: " + session['username'] + " delete comment")
                else:
                    return "You do not have permission to delete this comment.", 403
                
                return redirect(f'/product?id={id}')

            if request.method == "POST":
                if "username" in session: 
                    user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
                    userid = user_info[0]
                    url = request.form.get("stockapi")
                
                    response = requests.get(url)
                    raw_html = response.text
                
                    return raw_html
        
                    if "item is in stock" in response.text:
                        if db.session.execute(text(f"SELECT * FROM cart_items WHERE user_id = {userid} and product_id = {product_info['id']}")).fetchone() == None:

                            db.session.execute(text(f"INSERT INTO cart_items (user_id , product_id) VALUES({userid},{product_info['id']}) "))
                            db.session.commit()
                            print(f"add item: {product_info['name']}")
                            return  redirect(f"/product?id={product_info['id']}")
                        else:
                            print("you cant buy item twise")
                            return  redirect(f"/product?id={product_info['id']}")
                    elif "item is out of stock" in response.text:
                        return render_template('product.html', product=product_info, comments=comments_list, in_stock=False)
           
                else:   
                    return "you are not authorized user, please <a href='/login'>login</a>", 401
        
        session_username = session.get('username', None)
        return render_template('product.html', product=product_info, comments=comments_list, in_stock=True, session_username=session_username)

    else:
        return "id not provided"

@app.route('/cart', methods=['POST', "GET"])
def cart():
    if "username" in session:
        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
        userid = user_info[0]

        cart_items_records = db.session.execute(text(f"SELECT * FROM cart_items WHERE user_id = '{userid}'")).fetchall()
        items_for_template = []
        total_price = 0
        for item in cart_items_records:
            #INJCTION
            P = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
            #INJCTION
            product_details = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
            #INJCTION
            quntity = db.session.execute(text(f"SELECT * from cart_items WHERE user_id = {userid} AND product_id =  {item[2]}")).fetchone()
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
            db.session.execute(
                #INJCTION
                text(f"DELETE FROM cart_items WHERE user_id = '{userid}' AND product_id = '{item_id_to_remove}'")
            )
            db.session.commit()
            item = db.session.execute(
                #INJCTION
                text(f"SELECT * FROM products WHERE id = '{item_id_to_remove}'")
            ).fetchone()
            db.session.commit()
            return  redirect(f"/cart")
        
        if request.method == "POST" and "productid_increase" in request.form:
            db.session.execute(
                #INJCTION
                text(f"UPDATE cart_items SET quantity = quantity + {request.form.get("quantity")} WHERE user_id = {userid} AND product_id = {request.form['productid_increase']}")
            )
            db.session.commit()
            return  redirect(f"/cart")
        if request.method == "POST" and "productid_dcrease" in request.form:
            db.session.execute(
                #INJCTION
                text(f"UPDATE cart_items SET quantity = quantity - {request.form.get("quantity")} WHERE user_id = {userid} AND product_id = {request.form['productid_dcrease']}")
            )
            if db.session.execute(
                #INJCTION
                text(f"SELECT quantity FROM cart_items WHERE user_id = {userid} AND product_id = {request.form['productid_dcrease']}")
            ).fetchone()[0] == 0:
                db.session.execute(
                    #INJCTION
                    text(f"DELETE FROM cart_items WHERE user_id = {userid} AND product_id = {request.form['productid_dcrease']}")
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
    if "username" in session:
        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
        userid = user_info[0]
        user_cash = user_info[5]
        
        cart_items_records = db.session.execute(text(f"SELECT * FROM cart_items WHERE user_id = '{userid}'")).fetchall()
        
        if not cart_items_records:
            return redirect(url_for('cart'))
        
        total_price = 0
        Sorder_id = 0
        products_data_in_cart = []

        for item in cart_items_records:
            P = db.session.execute(text(f"SELECT * FROM products WHERE id = '{item[2]}'")).fetchone()
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
        db.session.execute(text(f"UPDATE users SET money = {user_cash} WHERE id = {userid}"))
        db.session.execute(text(f"DELETE FROM cart_items WHERE user_id = '{userid}'"))
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


@app.route('/admin_login', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('adminname')
        password = request.form.get('password')   
        hashed_input_password = MD5.new(password.encode()).hexdigest()
            
        #INJCTION
        query_string = f"SELECT * FROM admins WHERE name = '{username}' AND password = '{hashed_input_password}'"
        result = db.session.execute(text(query_string)).fetchone()
        if result:
            session['admin_name'] = username 
            #flash("Admin login successful!", "success")
            return redirect(url_for('admin_panal'))
        else:
            #flash("Invalid admin credentials.", "error")
            return redirect(url_for('admin')) 
    return render_template('admin_login.html')

@app.route('/admin_panal', methods=['POST', 'GET'])
def admin_panal():
    if 'admin_name' not in session:
       return redirect(url_for('login'))

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
                log_content = "Error"
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
    with open('log.txt', 'a') as log_file:
        log_file.write("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"+ '\n')
        log_file.write(message + '\n')

if __name__ == "__main__":
    app.run(debug=True, port=5000,host="0.0.0.0")