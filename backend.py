from flask import Flask, render_template,request, redirect, url_for, session,  flash
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2



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

    if "username" in session:
        products = db.session.execute(text("SELECT * FROM products WHERE show_on_page = 1")).fetchall()    
        return render_template('index.html', username=session["username"], products=products)
    
    return render_template('index.html')



@app.route('/login',methods=['GET', 'POST'])
def login_page():
    if request.method  == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')        
        hashed_input_password = MD5.new(password.encode()).hexdigest()
         # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
        query_string = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_input_password}'"
        query = text(query_string)
        result = db.session.execute(query).fetchone()

        if result: 
            session.clear() 
            session['username'] = username
            return redirect(url_for('user_page'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login_page'))
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
            result2 = db.session.execute(text(db_quary)).fetchone()
            if submitted_answer == result2[0]:
                
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
                db_quary = f"SELECT security_question FROM users WHERE username = '{username}'"
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
                db_password =  db.session.execute(text(db_password_quray)).fetchone()
                if MD5.new(current_password .encode()).hexdigest() == db_password[0]:
                    if new_password == confirm_password:
                        db_query = f"UPDATE users SET password = '{MD5.new(new_password .encode()).hexdigest()}' WHERE username = '{current_user}'"
                        db.session.execute(text(db_query))
                        db.session.commit()
                        message = {
                            "text": "Password reset successfully",
                            "color": "green"
                        }
                        flash("Password reset successfully","info")
                        return redirect(url_for('user_page'))
                        #return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
                    else:
                        message = {
                            "text": "Passwords do not match",
                            "color": "red"
                        }
                    flash("Passwords do not match","error")
                    return redirect(url_for('user_page'))
                    #return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
                else:
                        message = {
                            "text": "current password not match",
                            "color": "red"
                        }
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
    category_options = ["Computer","Game","Software","Peripheral","All"]
    catagory = request.args.get('category')
    user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
    if catagory not in category_options or catagory == category_options[4]:
        items = db.session.execute(text("SELECT * FROM products")).fetchall()
        return render_template('products.html', products=items,catagory=category_options[4],user_cash=user_info[5])
    if catagory ==  category_options[0]:
        items = db.session.execute(text(f"SELECT * FROM products WHERE category = '{category_options[0]}'")).fetchall()
        return render_template('products.html', products=items,catagory=category_options[0],user_cash=user_info[5])
    if catagory == category_options[1]:
        items = db.session.execute(text(f"SELECT * FROM products WHERE category = '{category_options[1]}'")).fetchall()
        return render_template('products.html', products=items,catagory=category_options[1],user_cash=user_info[5])
    if catagory ==  category_options[2]:
        items = db.session.execute(text(f"SELECT * FROM products WHERE category = '{category_options[2]}'")).fetchall()
        return render_template('products.html', products=items,catagory=category_options[2],user_cash=user_info[5])
    if catagory == category_options[3]:
        items = db.session.execute(text(f"SELECT * FROM products WHERE category = '{category_options[3]}'")).fetchall()
        return render_template('products.html', products=items,catagory=category_options[3],user_cash=user_info[5])

#מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד 

@app.route('/product',methods=['GET', 'POST'])
def product():
        id = request.args.get('id')
        if id:
            product= db.session.execute(text(f"SELECT * FROM products WHERE id = '{id}'")).fetchone()
            prodact_info = {
                "id": product[0]
                ,"name":product[1]
                ,"price":product[3]
                ,"release_date": product[2]
                ,"image_url": product[4]
            }
            
            if request.method == "POST" and request.form.get("add_to_cart"):
                if "username" in session: 
                        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
                        userid = user_info[0]
                        print(userid)
                        if db.session.execute(text(f"SELECT * FROM cart_items WHERE user_id = {userid} and product_id = {prodact_info['id']}")).fetchone() == None:
                            print(userid)
                            db.session.execute(text(f"INSERT INTO cart_items (user_id , product_id) VALUES({userid},{prodact_info['id']}) "))
                            db.session.commit()
                            print(f"add item: {prodact_info['name']}")
                            return  redirect(f"/product?id={prodact_info['id']}")
                        else:
                            print("you cant buy item twise")
                            return  redirect(f"/product?id={prodact_info['id']}")
                else:
                    return "you are not authorized user, please <a href='/login'>login</a>", 401

            
            return render_template('product.html', product_name=prodact_info["name"],
                                   product_price=prodact_info["price"],
                                   img=prodact_info["image_url"],product_release_date= prodact_info["release_date"])

        else:
            return "id not init"



@app.route('/cart', methods=['POST', "GET"])
def cart():
    if "username" in session:
        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
        userid = user_info[0]

        cart_items_records = db.session.execute(text(f"SELECT * FROM cart_items WHERE user_id = '{userid}'")).fetchall()
        items_for_template = []
        total_price = 0
        for item in cart_items_records:
            P = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
            product_details = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
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
                text(f"DELETE FROM cart_items WHERE user_id = '{userid}' AND product_id = '{item_id_to_remove}'")
            )
            db.session.commit()
            item = db.session.execute(
                text(f"SELECT * FROM products WHERE id = '{item_id_to_remove}'")
            ).fetchone()
            db.session.commit()
            return  redirect(f"/cart")
        
        if request.method == "POST" and "productid_increase" in request.form:
            db.session.execute(
                text(f"UPDATE cart_items SET quantity = quantity + {request.form.get("quantity")} WHERE user_id = {userid} AND product_id = {request.form['productid_increase']}")
            )
            db.session.commit()
            return  redirect(f"/cart")
        if request.method == "POST" and "productid_dcrease" in request.form:
            db.session.execute(
                text(f"UPDATE cart_items SET quantity = quantity - {request.form.get("quantity")} WHERE user_id = {userid} AND product_id = {request.form['productid_dcrease']}")
            )
            if db.session.execute(
                text(f"SELECT quantity FROM cart_items WHERE user_id = {userid} AND product_id = {request.form['productid_dcrease']}")
            ).fetchone()[0] == 0:
                db.session.execute(
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
    
@app.route('/cart/checkout', methods=['POST',"GET"])
def chackout():
    if "username" in session:
        Sorder_id = False
        user_info = db.session.execute(text(f"SELECT * FROM users WHERE username = '{session['username']}'")).fetchone()
        userid = user_info[0]
        user_cash = user_info[5]
        cart_items_records = db.session.execute(text(f"SELECT * FROM cart_items WHERE user_id = '{userid}'")).fetchall()
        total_price = 0
        for item in cart_items_records:
            P = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
            if P[0] == 2:
                Sorder_id = True
            total_price += P[3] * item[3]
            print("P:",P)
            print("S:",Sorder_id)
        if total_price > user_cash:
            flash("you dont have enough monnay","info")
            print("you dont have enough monnay")
            return redirect(url_for('cart')) 
        elif total_price < 0:
            flash("total cant be 0","info")
            return redirect(url_for('cart')) 

        else:
            items_for_template = []
            order_id = ""
            if Sorder_id == False:
                for item in cart_items_records:
                    order_id += "i=" + str(item[2]) + ","
            
                order_id = MD5.new(order_id .encode()).hexdigest()
                print(order_id,"your order id: ")
            else:
                order_id = "amiga500"
                order_id = MD5.new(order_id .encode()).hexdigest()
                print(order_id,"your order id: ")

            
            user_cash = user_cash - total_price
            db.session.execute(text(f"UPDATE users SET money = {user_cash} WHERE id = {userid}"))
            db.session.commit()
           
            items_for_template = []
            for item in cart_items_records:
                P = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
                product_details = db.session.execute(text(f"SELECT * FROM products WHERE id = '{ item[2]}'")).fetchone()
                quntity = db.session.execute(text(f"SELECT * from cart_items WHERE user_id = {userid} AND product_id =  {item[2]}")).fetchone()
                product_data = {
                    "id": product_details[0],
                    "name": product_details[1],
                    "price": product_details[3],
                    "image_url": product_details[4],
                    "quantity": quntity[3]
                }
                items_for_template.append(product_data)
            db.session.execute(text(f"DELETE FROM cart_items WHERE user_id = '{userid}'"))
            db.session.commit()

            return render_template("checkout.html",
                                   total=total_price,
                                   user_name=user_info[1],
                                   user_cash=user_info[5],order_id=order_id,ordered_items=items_for_template)
    else:
        return "you are not authorized user, please <a href='/login'>login</a>", 401


@app.route('/dogs', methods=['POST', 'GET'])
def dogs():
    img_url = None

    if request.method == "POST":
        # קבלת ה-URL מהטופס שהמשתמש שלח (hidden input בשם 'api')
        api_url = request.form.get("api")

        # שולחים בקשת GET ל-API לקבלת תמונה של כלב אקראי
        try:
            response = requests.get(api_url) # כאן לוקחים קלט של משתמש בתור לינק
        except:
            return "Faild to reach API"

        if response.ok and "message" in response.json():
             #כאן בודקים אם זה הapi על ידי בדיקה אם התגובה מכילה את המילה הודעה
            json = response.json()# אם זה כן ממרים את זה לjson
            img_url = json["message"] # מפצלים את הjson ומשגים את הurl של התמונה 
            return render_template("dog.html", img_src=img_url) #מרנדרים את הדף עם הurl של התמונה
        else:
            return response.text, response.status_code

    return render_template("dog.html")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')   
        hashed_input_password = MD5.new(password.encode()).hexdigest()
        
        query_string = f"SELECT * FROM admins WHERE username = '{username}' AND password = '{hashed_input_password}"
        result = db.session.execute(text(query_string)).fetchone()
        if result:
            session['username'] = username
            return "YOU ARE ADMIN"
    return render_template('admin_panal.html')




if __name__ == "__main__":
    app.run(debug=True, port=5000,host="0.0.0.0")