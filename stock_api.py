from flask import Flask, render_template,request, redirect, url_for, session,  flash,request, jsonify,abort
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import requests
from Crypto.Hash import MD5,MD2
import random

app = Flask(__name__)

possible_ids = list(range(1, 18))

possible_ids.remove(2)


out_of_stock_ids = random.sample(possible_ids, 5)
out_of_stock_ids.append(99) 


def disable_all_stock():
    out_of_stock_ids.clear()
    for y in range(41): 
        out_of_stock_ids.append(y)



@app.route('/chackstock', methods=['GET'])
def chackstock():
    id = request.args.get('item_id', type=int) 
    
    if id in out_of_stock_ids :
        return "item is out of stock"
    else:
        return "item is in stock"

# The only change: Added this endpoint to make the function callable from the other service
@app.route('/trigger/disable_all_stock', methods=['POST'])
def trigger_disable_stock():
    disable_all_stock()
    return jsonify(status="success", message="All items have been marked as out of stock."), 200
 
if __name__ == "__main__":
    app.run(debug=True, port=8200,host="0.0.0.0")