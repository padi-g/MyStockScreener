from flask import Flask, render_template
from flaskext.mysql import MySQL
import quandl

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'MySql@123'
app.config['MYSQL_DATABASE_DB'] = 'stocks'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

pharma = {'ACC', 'AMBUJACEM', 'HEIDELBERG', 'INDIACEM'}

# ACC, Ambuja, Heidelberg cem, India cements, JK Cements, Ramco, Ultratech, Dalmia
@app.route("/")
def main():
    return render_template('index.html')


@app.route("/quickstart")
def quickstart():
    # show best performing stocks from each sector for the last close
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("DESCRIBE EMPLOYEE;")
    data = cursor.fetchall()
    return str(data)

@app.route("/sector/")  # variable sector names
def sectors():
    mydata = quandl.get(["NSE/OIL.1", "WIKI/AAPL.4"], rows=5)

if __name__ == "__main__":
    app.run()