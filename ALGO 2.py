"""

@author: Luca
"""

import requests
import math
from time import sleep

# set your API key to authenticate to the RIT client
API_KEY = {'X-API-Key': 'YOUR API KEY HERE'}

# other settings for market making algo
SPREAD = 0.02
BUY_VOLUME = 500
SELL_VOLUME = 500
RISK_BOUND = 1500
RISK_LIMIT = 4000

# this helper method returns the current 'tick' of the running case
def get_tick(session):
    resp = session.get('http://localhost:9999/v1/case')
    
    case = resp.json()
    return case['tick']

# this helper method returns the last close price for the given security, one tick ago
def ticker_close(session, ticker):
    payload = {'ticker': ticker, 'limit': 1}
    resp = session.get('http://localhost:9999/v1/securities/history', params=payload)
    
    ticker_history = resp.json()
    if ticker_history:
        return ticker_history[0]['close']
    
#this helper method returns the current order book
def bidask(s,ticker):
    
    par={"ticker":ticker, "limit":50}
    
    data=s.get("http://localhost:9999/v1/securities/book", params=par).json()
    
    bid=[(x["price"],x["quantity"])for x in data["bids"]]
    ask=[(x["price"],x["quantity"])for x in data["asks"]]
    
    return (bid, ask)


# this helper method submits a pair of mkt orders to liquidate the current position
def buy(session, to_buy, BUY_volume):
   
    # actual part where you send order to RIT
    buy_payload = {'ticker': to_buy, 'type': 'MARKET', 'quantity': BUY_volume, 'action': 'BUY'}
    session.post('http://localhost:9999/v1/orders', params=buy_payload)


# this helper method submits a pair of mkt orders to liquidate the current position
def sell(session, to_sell, SELL_volume):
   
    # actual part where you send order to RIT
    sell_payload = {'ticker': to_sell, 'type': 'MARKET', 'quantity': SELL_volume, 'action': 'SELL'}
    
    session.post('http://localhost:9999/v1/orders', params=sell_payload)
    
    
# this helper method submits a pair of limit orders to buy and sell VOLUME of each security, at the last price +/- SPREAD
def buy_sell(session, to_buy, to_sell, last):
    buy=last-SPREAD
    sell=last+SPREAD
    
    # this part convert the buy and the sell float variables into string with the "," and not "."
    buy_truncated = math.floor(buy * 100) / 100
    buy_str = f"{buy_truncated:.2f}"
    buy_str = buy_str.replace(".", ",")
    
    sell_truncated = math.floor(sell * 100) / 100
    sell_str = f"{sell_truncated:.2f}"
    sell_str = sell_str.replace(".", ",")
    
    # actual part where you send order to RIT
    buy_payload = {'ticker': to_buy, 'type': 'LIMIT', 'quantity': BUY_VOLUME, 'action': 'BUY', 'price': buy_str}
    sell_payload = {'ticker': to_sell, 'type': 'LIMIT', 'quantity': SELL_VOLUME, 'action': 'SELL', 'price': sell_str}
    session.post('http://localhost:9999/v1/orders', params=buy_payload)
    session.post('http://localhost:9999/v1/orders', params=sell_payload)

# this helper method gets all the orders of a given type (OPEN/TRANSACTED/CANCELLED)
def get_orders(session, status):
    payload = {'status': status}
    resp = session.get('http://localhost:9999/v1/orders', params=payload)

    orders = resp.json()
    return orders

# this helper method gets our current position (LONG / SHORT) in ALGO share
def position(s):
    payload={'ticker':"ALGO"}
    resp = s.get('http://localhost:9999/v1/securities', params=payload)
    secs= resp.json()
   
    return secs[0]["position"]
    
# this helper method gets our current cost of the position
def cost(s):
    payload={'ticker':"ALGO"}
    resp = s.get('http://localhost:9999/v1/securities', params=payload)
    average_cost= resp.json()
    
    return average_cost[0]["vwap"]
        
    

# this is the main method containing the actual market making strategy logic
def ses(s):
    
    # get the open order book and ALGO last tick's close price
    orders = get_orders(s, 'OPEN')
    algo_close = ticker_close(s, 'ALGO')

    # check if you have 0 open orders
    if len(orders) == 0:
        # submit a pair of orders and update your order book
        buy_sell(s, 'ALGO', 'ALGO', algo_close)
        orders = get_orders(s, 'OPEN')
        sleep(1)

    # check if you don't have a pair of open orders
    if len(orders) != 2 and len(orders) > 0:
        # submit a POST request to the order cancellation endpoint to cancel all open orders
        s.post('http://localhost:9999/v1/commands/cancel?all=1')
        sleep(1)
        
    # check our current position (LONG / SHORT) and liquidate it in profit
    pos=position(s)
    if abs(pos) >= RISK_BOUND and abs(pos) <= RISK_LIMIT:
        bid,ask = bidask (s, "ALGO")
        average = cost(s)
        if pos < 0:
            new_pos = int(abs(pos))
            if average > ask[0][0]:
                buy(s,"ALGO",new_pos)
                print("we have bought", new_pos," share at",ask[0][0], "while vwap was",average)
                sleep(1)
        else:
            new_pos = int(abs(pos))
            if average < bid[0][0]:
                sell(s,"ALGO",new_pos)
                print("we have sold", new_pos," share at",bid[0][0], "while vwap was",average)
                sleep(1)
                
    # if |current position| goes beyond RISK_LIMIT we buy or sell 1000 shares until we are below RISK_LIMIT
    if abs(pos) > RISK_LIMIT:
        if pos<0:
            buy(s,"ALGO",1000)
            print("TOO MUCH EXPOSURE: try to return in our bound, bought 1000")
            sleep(1)
        else:
            sell(s,"ALGO",1000)
            print("TOO MUCH EXPOSURE: try to return in our bound, sold 1000")
            sleep(1)
                
                
# creates a session to manage connections and requests to the RIT Client
s=requests.Session()
s.headers.update(API_KEY)


tick=get_tick(s)

# while the time is between 5 and 295, do the following
while tick > 1 and tick < 295:
    ses(s)
    tick=get_tick(s)
