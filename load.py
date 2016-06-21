"""
Elite Trading Tool Companion
http://elitetradingtool.co.uk/
"""

import sys
import ttk
import Tkinter as tk
import myNotebook as nb
import json
import requests
from threading import Thread


def plugin_start():
    console("Starting Elite Trading Tool Companion")

def plugin_app(parent):
    plugin_app.parent = parent
    # VARIABLES
    plugin_app.lastSystem = None
    plugin_app.requestThread = None
    plugin_app.trade = None
    plugin_app.popup = None
    plugin_app.updateBtn = tk.Button(parent, text="Find trade", command=getBestTrade, state="disabled", width=16)
    plugin_app.updateBtn.grid(row=0,column=0)
    plugin_app.infoBtn = tk.Button(parent, text="Show", command=showBestTrade, state="disabled", width=16)
    plugin_app.infoBtn.grid(row=0,column=1)

def cmdr_data(data):
    cmdr_data.last = data
    plugin_app.lastSystem = data['lastSystem']['name']
    plugin_app.updateBtn['state'] = "normal"

def system_changed(timestamp, system, coordinates):
    plugin_app.lastSystem = system

def console(text):
    sys.stderr.write(text + "\n")

def setStatus(status):
    plugin_app.updateBtn['text'] = status

def getBestTrade():
    if cmdr_data.last is not None:
        plugin_app.updateBtn['state'] = "disabled"
        plugin_app.infoBtn['state'] = "disabled"
        setStatus("Searching Trade...")
        plugin_app.requestThread = Thread(target=doRequest)
        plugin_app.requestThread.start()
    else:
        setStatus("Please update.")

def showBestTrade():
    generatePopup(plugin_app.trade)

def doRequest():
    payload = {
        "SearchRange": "20",
        "SystemName": plugin_app.lastSystem,
        "ExcludePlanets":"true",
        "MaxDistanceFromJumpIn":"400",
        "MaxDistanceBetweenSystems":"19"
    }
    console("Sending payload.")
    r = requests.post('http://elitetradingtool.co.uk/api/EliteTradingTool/FindTrades', json=payload, headers={'Referer':'http://elitetradingtool.co.uk'})
    console("Status code: " + str(r.status_code))
    if r.status_code is 200:
        if (len(r.json()['List']) > 0):
            plugin_app.trade = r.json()['List'][0]
            plugin_app.infoBtn['state'] = "active"
        else:
            plugin_app.updateBtn['state'] = "active"
            plugin_app.infoBtn['text'] = "No trade found !"
    else:
        setStatus("Error:" + r.status_code)
    plugin_app.updateBtn['state'] = "normal"
    plugin_app.updateBtn['text'] = "Find trade"

def generatePopup(trade):
    if plugin_app.popup is not None:
        plugin_app.popup.destroy()
    plugin_app.popup = tk.Toplevel(plugin_app.parent)
    plugin_app.popup.wm_title("Elite Trading Tool info")
    plugin_app.popup.wm_attributes('-topmost', 1)
    text = tk.Label(plugin_app.popup)

    text['text'] = ("{SOURCE} {SOURCEDIST} {OUTGOINGCOMMODITY}"+
    "\n--> {DESTINATION} {DESTINATIONDIST}"+
    "\nBuy: {OUTBUYPRICE} ({OUTBUYUPDATE})"+
    "\nSell: {OUTSELLPRICE} ({OUTSELLUPDATE})"+
    "\nProfit: {OUTPROFIT}"+
    "\n-------------------"+
    "\n{DESTINATION} {DESTINATIONDIST} {RETURNINGCOMMODITY}"+
    "\n--> {SOURCE} {SOURCEDIST}"+
    "\nBuy: {RETBUYPRICE} ({RETBUYUPDATE})"+
    "\nSell: {RETSELLPRICE} ({RETSELLUPDATE})"+
    "\nProfit: {RETPROFIT}"+
    "\n\nTOTAL PROFIT: {TOTALPROFIT}").format(
        SOURCE = trade['Source'],
        SOURCEDIST = str(trade['SourceStationDistance'])+"ls",
        OUTGOINGCOMMODITY = trade['OutgoingCommodityName'],
        DESTINATION = trade['Destination'],
        DESTINATIONDIST = str(trade['DestinationStationDistance']) + "ls",
        OUTBUYPRICE = str(trade['OutgoingBuy']),
        OUTBUYUPDATE = trade['OutgoingBuyLastUpdate'],
        OUTSELLPRICE = str(trade['OutgoingSell']),
        OUTSELLUPDATE = trade['OutgoingSellLastUpdate'],
        OUTPROFIT = str(trade['OutgoingProfit']),
        RETURNINGCOMMODITY = trade['ReturningCommodityName'],
        RETBUYPRICE = str(trade['ReturningBuy']),
        RETBUYUPDATE = trade['ReturningBuyLastUpdate'],
        RETSELLPRICE = str(trade['ReturningSell']),
        RETSELLUPDATE = trade['ReturningSellLastUpdate'],
        RETPROFIT = str(trade['ReturningProfit']),
        TOTALPROFIT = str(trade['TotalProfit'])) + "/t (" + str(cmdr_data.last['ship']['cargo']['capacity']*trade['TotalProfit']) + ")"
    text.pack(side="top", pady=10, padx=10)

cmdr_data.last = None
