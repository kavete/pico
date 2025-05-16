import network
import urequests
import time
import secrets

ssid= secrets.SSID
password = secrets.PASSWORD

def connect():
    wlan= network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while wlan.isconnected() == False:
        print("Connecting, Please wait")
        time.sleep(1)
    print("Connected! IP = ", wlan.ifconfig()[0])
    
try:
    connect()
    site = "http://date.jsontest.com"
    
    print("Query: ", site )
    r = urequests.get(site)
    
    print(r.json())
    r.close()
except OSError as e:
    print("Error: Connection closed")
    