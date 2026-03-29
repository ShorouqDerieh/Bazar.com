from flask import Flask
from flask import jsonify #for json response
from flask import request
import sqlite3
app = Flask(__name__)
conn = sqlite3.connect("bazar.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT,topic TEXT,price REAL,quantity INTEGER)")

c.execute("INSERT OR IGNORE INTO books VALUES (1,'How to get a good grade in DOS in 40 minutes a day','distributed systems',20.0,100)")
c.execute("INSERT OR IGNORE INTO books VALUES (2,'RPCs for Noobs','distributed systems',50.0,200)")
c.execute("INSERT OR IGNORE INTO books VALUES (3,'Xen and the Art of Surviving Undergraduate School','undergraduate school',30.0,150)")
c.execute("INSERT OR IGNORE INTO books VALUES (4,'Cooking for the Impatient Undergrad','undergraduate school',20.0,100)") 
conn.commit()
conn.close()
@app.route('/search/<string:topic>')
def get_books(topic):
    conn = sqlite3.connect("bazar.db",check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE topic=?",(topic,))
    books=c.fetchall()
    if not books:
        conn.close()
        return jsonify({"error":"No books found for this topic"}),404
    returned_books=[]
    for book in books:
        returned_books.append({
            "id":book[0],
            "title":book[1],
            "topic":book[2],
            "price":book[3],
            "quantity":book[4]
        })
    conn.close()
    return jsonify(returned_books)  
@app.route("/search/<int:id>")
def get_book_by_id(id):
    conn = sqlite3.connect("bazar.db",check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id=?",(id,))
    book=c.fetchone()
    if book:
        returned_book={
            "id":book[0],
            "title":book[1],
            "topic":book[2],
            "price":book[3],
            "quantity":book[4]
        }
        conn.close()
        return jsonify(returned_book)
    else:
        conn.close()
        return jsonify({"error":"Book not found"}),404
@app.route("/update")
def update_book():
    conn = sqlite3.connect("bazar.db",check_same_thread=False)
    c = conn.cursor()
    id=request.json.get("id")
    quantity=request.json.get("quantity")
    price=request.json.get("price")
    if quantity:
        c.execute("UPDATE books SET quantity=? WHERE id=?",(quantity,id))
        return jsonify({"message":"Book quantity updated"})
    if price:
        c.execute("UPDATE books SET price=? WHERE id=?",(price,id))
        return jsonify({"message":"Book price updated"})
        if not id:
            conn.close()
            return jsonify({"error":"Book id is required"}),400
    conn.commit()
    conn.close()