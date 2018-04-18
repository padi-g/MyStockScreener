from flask import Flask, render_template, send_file, request
from flaskext.mysql import MySQL
import quandl
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import random
import datetime
from matplotlib.dates import (YEARLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import pandas as pd

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'MySql@123'
app.config['MYSQL_DATABASE_DB'] = 'stocks'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

pharma = ['AARTIDRUGS', 'AJANTPHARM', 'SUNPHARMA', 'BIOCON', 'CIPLA', 'DRREDDY', 'GLAXO', 'PFIZER']
cement = ['ACC', 'AMBUJACEM', 'HEIDELBERG', 'INDIACEM', 'DALMIABHA', 'JKCEMENT', 'RAMCOCEM', 'ULTRACEMCO']
infotech = ['HCLTECH', 'INFY', 'TCS', '8KMILES', 'MINDTREE', 'MPHASIS', 'TECHM', 'NIITTECH']
banking = ['SBIN', 'AXISBANK', 'BANDHANBNK', 'HDFCBANK', 'ICICIBANK', 'KARURVYSYA', 'YESBANK', 'KOTAKBANK']
food = ['BRITANNIA', 'COFFEEDAY', 'HATSUN', 'HERITGFOOD', 'KOHINOOR', 'KWALITY', 'VADILALIND', 'FCONSUMER']
misc = ['FINPIPE', 'PIDILITIND', 'GIPCL', 'POWERGRID', 'SCHNEIDER', 'TORNTPOWER', 'KALPATPOWR', 'KEC']


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/overview")
def overview():
    # show best performing stocks from each sector for the last close

    cursor.execute("DESCRIBE EMPLOYEE;")
    data = cursor.fetchall()
    return str(data)


@app.route('/fig/<stock>')
def fig(stock):
    fi = graph_content(stock)
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route('/test', methods=['GET', 'POST'])
def samplefunction():
    stock = "GGG"
    if request.method == 'GET':
        return render_template('images.html', title=stock)
    if request.method == 'POST':
        greetIn = ['hey', 'hi', 'hey there', 'hi there', 'hello', 'hola', 'yoo']
        byeIn = ['bye', 'see you later', 'catch you later', 'toodles']
        nameOut = ['my name is Fatty!!', 'Fatty is my name', 'you can call me Fatty', 'I go by the name of Fatty']
        greetOut = ['hey there!', 'hi!', 'hi there!', 'hey!']
        byeOut = ['bye bye', 'bye. see you later']

        human1 = request.form['human']

        if human1 in greetIn:
            bot = random.choice(greetOut)
            return render_template('images.html', bot=bot, title=stock)
        else:
            bot = 'Sorry..no idea!!!'
            return render_template('images.html', bot=bot, title=stock)


@app.route('/sector/<sector>')
def open_sector_page(sector):
    stocklist = []
    if sector == 'pharma':
        stocklist = pharma
    elif sector == 'infotech':
        stocklist = infotech
    elif sector == 'cement':
        stocklist = cement
    elif sector == 'banking':
        stocklist = banking
    elif sector == 'food':
        stocklist = food
    elif sector == 'misc':
        stocklist = misc

    return render_template('sector.html', title=sector, data=stocklist, extra='iol''''update_stock('iol')''')


def draw_polygons(stock):
    '''
    :param stock: stock SYMBOL
    :return: the graph figure
    '''
    s = stock
    figure = plt.plot([1, 2, 3, 4], [1, 2, 3, 4])
    return figure


def graph_content(symbol):
    query1 = "SELECT trading_date from OIL"
    query2 = "SELECT close from OIL"
    cursor.execute(query1)
    data1 = cursor.fetchall()
    cursor.execute(query2)
    data2 = cursor.fetchall()
    print(data1, data2)
    plt.xlabel("Close value")
    plt.ylabel("Date")
    plt.xticks(rotation=10)
    figure = plt.plot(data1, data2)
    return figure


def get_stock_data(stock, duration):
    update_stock(stock)
    query = "SELECT * FROM " + stock + ";"
    cursor.execute(query)
    data = cursor.fetchall()
    print(data)


def get_hundred():
    apidata = quandl.get(["NSE/OIL"], rows=10)
    apidata.reset_index()
    print(apidata.ix[:, 0])
    columns = apidata.columns.values.tolist()
    rows = apidata.index.values
    for row in rows:
        tup = []
        tup.append(str(row)[0:10])
        for column in columns:
            tup.append(apidata.loc[row, column])
        query = "INSERT INTO OIL VALUES('" + str(tup[0]) + "', " + str(tup[1]) + ", " + str(tup[2]) + ", " + str(tup[3]) + ", " + str(tup[4]) \
                + ", " + str(tup[5]) + ", " + str(tup[6]) + ", " + str(tup[7]) + ");"
        cursor.execute(query)
        conn.commit()

        # insert into table


def update_stock(stock):
    # TODO : Setup trigger to update cache if new stock table is added or existing is updated
    query = "SELECT * FROM CACHE WHERE SYMBOL = '" + stock + "';"
    cursor.execute(query)
    data = cursor.fetchone()
    stock = 'iol'
    if data[0] == stock:
        d = datetime.date.today().strftime('%Y-%m-%d')
        if str(data[1]) == d:
            # up to date
            exit()
        else:  # update cache
            exit()
    return data


def test_get_cache():
    query = "SELECT * FROM CACHE;"
    cursor.execute(query)
    data = cursor.fetchall()
    print(data[0][0])
    return data


def create_new_table(symbol):
    query = "CREATE TABLE " + symbol + \
            "(trading_date date primary key, open decimal(10,2), close decimal(10,2), high decimal(10,2)," \
            " low decimal(10,2), last decimal(10,2), quantity decimal(10,2), turnover decimal(10,2));"
    cursor.execute(query)
    conn.commit()



# last 100 trading days data


def search_stock():
    exit()


if __name__ == "__main__":
    conn = mysql.connect()
    cursor = conn.cursor()
    graph_content('oil')
    app.run()

'''

    Functionality :
        landing page : clickable sectors and overview
                       search bar that recommends autocomplete
        overview : graph of last 5 days for biggest gain and biggest loss from each sector
        Sectoral pages :
                    Graph of last 100 days for all stocks in sector

    TODO :
        - Onclick sector, open sectoral html file
        - Find a template for the sectoral pages
        - is API key required?
        - onclick overview, open overview page
        - find template for overview page
        - find a way to display the sql queries directly on the page
        - figure out graphing

    Endpoints :

create table OIL(trading_date date primary key, open decimal(10,2), close decimal(10,2), high decimal(10,2), low decimal(10,2), last decimal(10,2), quantity decimal(10,2), turnover decimal(10,2));

'''
