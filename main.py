from flask import Flask, render_template, send_file, request
from flaskext.mysql import MySQL
import quandl
from io import BytesIO
import matplotlib.pyplot as plt
import random
import datetime

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
banking = ['SBIN', 'AXISBANK', 'CANBK', 'HDFCBANK', 'ICICIBANK', 'KARURVYSYA', 'YESBANK', 'KOTAKBANK']
food = ['BRITANNIA', 'COFFEEDAY', 'HATSUN', 'APEX', 'KOHINOOR', 'KWALITY', 'VADILALIND', 'FCONSUMER']
misc = ['FINPIPE', 'PIDILITIND', 'GIPCL', 'POWERGRID', 'SCHNEIDER', 'TORNTPOWER', 'KALPATPOWR', 'KEC']

prcnt_values = {'pharma': ["ACC", 0.0],
                'cement': ["ACC", 0.0],
                'infotech': ["ACC", 0.0],
                'banking': ["ACC", 0.0],
                'food': ["ACC", 0.0],
                'misc': ["ACC", 0.0]}


@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        search = request.form['search']
        print(search)
        query = "select symbol, name_of_company from companies where symbol " \
                "like '%" + search + "%' OR name_of_company like '%" + search + "%';"
        cursor.execute(query)
        data = cursor.fetchone()

        print(data)
        return render_template('search.html', search=data)


@app.route('/fig/<stock>')
def fig(stock):
    graph_content(stock)
    img = BytesIO()
    plt.savefig(img)
    plt.clf()
    img.seek(0)
    return send_file(img, mimetype='image/png')


def graph_content(symbol):
    update_stock(symbol)
    query1 = "SELECT trading_date from " + symbol
    query2 = "SELECT close from " + symbol
    cursor.execute(query1)
    data1 = cursor.fetchall()
    cursor.execute(query2)
    data2 = cursor.fetchall()
    plt.ylabel("Close value")
    plt.xlabel("Date")
    plt.xticks(rotation=10)
    plt.plot(data1, data2)


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


@app.route('/overview')
def overview():
    aid_overview()
    return render_template('overview.html', data=prcnt_values)


def update_stock(stock):
    query = "SELECT * FROM CACHE WHERE SYMBOL = '" + stock + "';"
    cursor.execute(query)
    data = cursor.fetchone()
    # exception thrown when table for stock is created but cache is not updates
    # because download failed from api key error
    #    what's happening if it actually is present??
    if data is None:
        create_new_table(stock)
    elif data[0] == stock:  # stock exists
        today = datetime.date.today().strftime('%Y-%m-%d')
        print(str(data[1]), today)
        if str(data[1]) != today:
            download_stock_data(stock, 100)
            #   What happens when you try to insert already existing values ??
            # no check if we actually have 100 data or not
    return data


def download_stock_data(stock, duration):
    # download from api
    apidata = quandl.get(["NSE/" + stock], rows=duration, api_key='J2zm7zF2_yzzDHEVcJjz')
    apidata.reset_index()
    print(apidata.ix[:, 0])
    columns = apidata.columns.values.tolist()
    rows = apidata.index.values
    for row in rows:
        tup = []
        tup.append(str(row)[0:10])
        # 10 or 100?
        for column in columns:
            tup.append(apidata.loc[row, column])
        query = "INSERT INTO " + stock + " VALUES('" + str(tup[0]) + "', " + str(tup[1]) + ", " + str(
            tup[2]) + ", " + str(tup[3]) + ", " + str(tup[4]) \
                + ", " + str(tup[5]) + ", " + str(tup[6]) + ", " + str(tup[7]) + ");"
        cursor.execute(query)
        conn.commit()
    update_cache(stock)


def update_cache(stock):
    '''
    insert if not already there, else update
    '''
    query = "SELECT SYMBOL FROM CACHE WHERE SYMBOL = '" + stock + "'"
    cursor.execute(query)
    data = cursor.fetchone()
    if data is None:
        query = "INSERT INTO CACHE VALUES('" + stock + "', + CURDATE());"
    else:
        query = "UPDATE CACHE SET LASTUPDATE = CURDATE() WHERE SYMBOL = '" + stock + "'"
    cursor.execute(query)
    conn.commit()


def create_new_table(symbol):
    query = "CREATE TABLE " + symbol + \
            "(trading_date date primary key, open decimal(10,2), close decimal(10,2), high decimal(10,2)," \
            " low decimal(10,2), last decimal(10,2), quantity decimal(10,2), turnover decimal(10,2));"
    cursor.execute(query)
    conn.commit()
    download_stock_data(symbol, 100)


def aid_overview():
    # max finding can be done much better
    # probably not the best choice of data structures, and ways of itereating through them
    percent_change = [[0.0] * 8]
    i = 0
    t = ['ACC', -1000]
    for comp in pharma:
        query = "SELECT close FROM " + comp + " ORDER BY TRADING_DATE DESC LIMIT 0,2"
        cursor.execute(query)
        data = cursor.fetchall()
        percent_change[i] = round((data[0][0] - data[1][0]) * 100 / data[0][0], 2)
        if percent_change[i] > t[1]:
            t = (comp, percent_change[i])
    prcnt_values['pharma'] = t
    i = 0
    t = ['ACC', -1000]
    for comp in cement:
        query = "SELECT close FROM " + comp + " ORDER BY TRADING_DATE DESC LIMIT 0,2"
        cursor.execute(query)
        data = cursor.fetchall()
        percent_change[i] = round((data[0][0] - data[1][0]) * 100 / data[0][0], 2)
        if percent_change[i] > t[1]:
            t = (comp,   percent_change[i])
    prcnt_values['cement'] = t
    i = 0
    t = ['ACC', -1000]
    for comp in infotech:
        query = "SELECT close FROM " + comp + " ORDER BY TRADING_DATE DESC LIMIT 0,2"
        cursor.execute(query)
        data = cursor.fetchall()
        percent_change[i] = round((data[0][0] - data[1][0]) * 100 / data[0][0], 2)
        if percent_change[i] > t[1]:
            t = (comp, percent_change[i])
    prcnt_values['infotech'] = t
    i = 0
    t = ['ACC', -1000]
    for comp in banking:
        query = "SELECT close FROM " + comp + " ORDER BY TRADING_DATE DESC LIMIT 0,2"
        cursor.execute(query)
        data = cursor.fetchall()
        percent_change[i] = round((data[0][0] - data[1][0]) * 100 / data[0][0], 2)
        if percent_change[i] > t[1]:
            t = (comp, percent_change[i])
    prcnt_values['banking'] = t
    i = 0
    t = ['ACC', -1000]
    for comp in food:
        query = "SELECT close FROM " + comp + " ORDER BY TRADING_DATE DESC LIMIT 0,2"
        cursor.execute(query)
        data = cursor.fetchall()
        percent_change[i] = round((data[0][0] - data[1][0]) * 100 / data[0][0], 2)
        if percent_change[i] > t[1]:
            t = (comp, percent_change[i])
    prcnt_values['food'] = t
    i = 0
    t = ['ACC', -1000]
    for comp in misc:
        query = "SELECT close FROM " + comp + " ORDER BY TRADING_DATE DESC LIMIT 0,2"
        cursor.execute(query)
        data = cursor.fetchall()
        percent_change[i] = round((data[0][0] - data[1][0]) * 100 / data[0][0], 2)
        if percent_change[i] > t[1]:
            t = (comp, percent_change[i])
    prcnt_values['misc'] = t


if __name__ == "__main__":
    conn = mysql.connect()
    cursor = conn.cursor()
    app.run(host='0.0.0.0')

'''

    Functionality :
        landing page : clickable sectors and overview
                       search bar that recommends autocomplete
        overview : graph of last 5 days for biggest gain and biggest loss from each sector
        Sectoral pages :
                    Graph of last 100 days for all stocks in sector

    TODO :
        - Onclick sector, open sectoral html file   ------
        - Find a template for the sectoral pages
        - is API key required?
        - onclick overview, open overview page
        - find template for overview page
        - find a way to display the sql queries directly on the page
        - figure out graphing   -----

    Endpoints :

TODO : EXCEPTIONS
TODO : Loading spinner

TODO : drop all tables and test again
TODO : document all problems
TODO : create readme for open sourcing and fudge database passwords
TODO : 5 DAY data load instead of 100

TODO : pressing home on overview page

'''
