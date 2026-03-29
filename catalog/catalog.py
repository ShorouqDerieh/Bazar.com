from flask import Flask
from flask import jsonify #for json response
import sqlite3
app = Flask(__name__)
conn = sqlite3.connect("bazar.db")
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS books (id INTEGER, title TEXT,topic TEXT,price REAL,quantity INTEGER)")

c.execute("INSERT OR IGNORE INTO books VALUES (1,'How to get a good grade in DOS in 40 minutes a day','distributed systems',20.0,100)")
c.execute("INSERT OR IGNORE INTO books VALUES (2,'RPCs for Noobs','distributed systems',50.0,200)")
c.execute("INSERT OR IGNORE INTO books VALUES (3,'Xen and the Art of Surviving Undergraduate School','undergraduate school',30.0,150)")
c.execute("INSERT OR IGNORE INTO books VALUES (4,'Cooking for the Impatient Undergrad','undergraduate school',20.0,100)") 
conn.commit()
conn.close()
app.run()
