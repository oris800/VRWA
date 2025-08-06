from flask import Flask, render_template,request, redirect, url_for, session
from user_model import User
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

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
        return render_template('index.html',username=session["username"])
    return render_template('index.html')



@app.route('/login',methods=['GET', 'POST'])
def login_page():
    if request.method  == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')        
        
         # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
        query_string = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        query = text(query_string)
        result = db.session.execute(query).fetchone()
        print(result)
        if result:
            session['username'] = username
            return redirect(url_for('user_page'))

        else:
            message = {
                "text": "Invalid username or password",
                "color": "red"
            }
            return render_template('login.html', message=message)
    return render_template('login.html')


#מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד מוצר יחיד 

@app.route('/product',methods=['GET', 'POST'])
def product():
        id = request.args.get('id')
        if not id:
            return "id not init"
        else:
            result_from_Db = db.session.execute(text("SELECT * FROM products WHERE id = " + str(id))).fetchone()
            product_name = result_from_Db[1]
            product_relase_date = result_from_Db[2]
            product_price = result_from_Db[3]
            product_img = result_from_Db[4]
            if request.method == "POST":
                userid_qury = db.session.execute(
                text(f"SELECT * FROM users WHERE username = '{session['username']}'")
                ).fetchone()
                user_id = userid_qury[0]
                dose_item_exist = db.session.execute(
                text("SELECT * FROM cart_items WHERE user_id = :user_id AND product_id = :product_id"),
                {"user_id": user_id, "product_id": id}
                ).fetchone()
                print(dose_item_exist)
                if dose_item_exist == None:
                    db.session.execute(text(f"INSERT INTO cart_items (user_id, product_id, quantity) VALUES ({user_id}, {id}, 1)"))
                    db.session.commit()
                    message = {
                            "text": "item has add to cart! go chack out your cart!!!",
                            "color": "green"
                        }
                    return render_template('product.html', product_name=product_name,product_price=product_price,product_release_date=product_relase_date,img=product_img,message=message)
                else:
                    message = {
                            "text": "you already bought the item",
                            "color": "red"
                    }
                return render_template('product.html', product_name=product_name,product_price=product_price,product_release_date=product_relase_date,img=product_img,message=message)
        return render_template('product.html', product_name=product_name,product_price=product_price,product_release_date=product_relase_date,img=product_img)
        

# מוצרים מוצרים  מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים מוצרים 

@app.route('/products',methods=['GET', 'POST'])
def products_page():
    items = db.session.execute(text("SELECT * FROM products")).fetchall()
    print(items)    
    if request.method == "POST":
        itemid = request.form.get("product_id")
        print(itemid)
        return redirect(f"/product?id={itemid}")
    return render_template('products.html', products=items)

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
                if current_password == db_password[0]:
                    if new_password == confirm_password:
                        db_query = f"UPDATE users SET password = '{new_password}' WHERE username = '{current_user}'"
                        db.session.execute(text(db_query))
                        db.session.commit()
                        message = {
                            "text": "Password reset successfully",
                            "color": "green"
                        }
                        return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
                    else:
                        message = {
                            "text": "Passwords do not match",
                            "color": "red"
                        }
                    return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
                else:
                        message = {
                            "text": "current password not match",
                            "color": "red"
                        }
                        return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5),message=message)
       
        return render_template('user.html',user_name=user_info[1],user_id=user_info[0],security_question=user_info[3],user_cash=user_info[5], user_name_encoded=caesar_cipher(username,5))
    else:
        return "you are not authorized user, please <a href='/login'>login</a>",401

@app.route('/reset',methods=['POST',"GET"])
def reset():
    if request.method == 'POST':
        username = request.form.get('username')
        if 'new_password' in request.form and session.get('can_reset_password'): #לא מובן לי המכינקה שמונעת עקיםת שלבים לחקור בהמשך
            
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
         
        
            # במסד נתונים לא לשכוח להצפין את הסיססמה!!!!
            if new_password == confirm_password:
                db_query = f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'"
                db.session.execute(text(db_query))
                db.session.commit()
                session.pop('can_reset_password', None)
                message = {
                    "text": "Password reset successfully",
                    "color": "green"
                }
                return render_template('login.html',message=message)
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

@app.route('/cart',methods=['POST',"GET"])
def cart():
    if "username" in session:
 
         return render_template("cart.html")
    else:
        return "you are not authorized user, please <a href='/login'>login</a>",401



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page')) 


if __name__ == "__main__":
    app.run(debug=True, port=5000,host="0.0.0.0")