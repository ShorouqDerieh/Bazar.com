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
    returned_books={}
    for book in books:
       """  returned_books.append({
            "id":book[0],
            "title":book[1],
            "topic":book[2],
            "price":book[3],
            "quantity":book[4]
        }) """
       returned_books[book[1]] = book[0]
       print(f"Book Title: {book[1]}, Book ID: {book[0]}")
    conn.close()
  #  return jsonify(returned_books)  
    return jsonify({"items": returned_books})
@app.route("/info/<int:id>")
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
@app.route("/update/<int:id>",methods=["PUT"])
def update_book(id):
    conn = sqlite3.connect("bazar.db",check_same_thread=False)
    c = conn.cursor()
    quantity=request.json.get("quantity")
    price=request.json.get("price")
    """ if not id:
            conn.close()
            return jsonify({"error":"Book id is required"}),400 """
    c.execute("SELECT quantity FROM books WHERE id = ?", (id,))
    result = c.fetchone()

    if not result:
     conn.close()
     return jsonify({"error": "Book not found"}), 404

    current_quantity = result[0]
    if quantity is not None:
        new_quantity = current_quantity + quantity
        if new_quantity < 0:
            conn.close()
            return jsonify({"error": "Quantity cannot be negative"}), 400
    updates = []
    params = []
    if quantity is not None:
        updates.append("quantity=quantity+?")
        params.append(quantity)
       # c.execute("UPDATE books SET quantity=? WHERE id=?",(quantity,id))
       # return jsonify({"message":"Book quantity updated"})
    if price is not None:
        updates.append("price=?")
        params.append(price)
        #c.execute("UPDATE books SET price=? WHERE id=?",(price,id))
        #return jsonify({"message":"Book price updated"})
    if not updates:
        conn.close()
        return jsonify({"error":"No updates provided"}),400
    params.append(id)
    q = "UPDATE books SET " + ", ".join(updates) + " WHERE id=?"
    c.execute(q,params)
    conn.commit()
    conn.close()
    return jsonify({"message":"Book updated successfully"})
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)