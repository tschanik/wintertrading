import os
import configparser
import requests
import json
import uuid
import time


def get_cookie():
	
	url = "https://comdirect.de"
	r = requests.get(url)
	s = "qSession"
	return s + "=" + dict(r.cookies)[s]


def check_status(access_token,guid_var,request_var,cookie):
	
	url = "https://api.comdirect.de/api/session/clients/user/v1/sessions"
	
	payload = {}
	headers = {
	  'Accept': 'application/json',
	  'Authorization': 'Bearer ' + access_token + '',
	  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
	  'Content-Type': 'application/json',
	  'Cookie': cookie
	}
	
	response = requests.request("GET", url, headers=headers, data=payload).json()
	
	return response


def auth(client_id,client_secret,username,password,cookie):

	url = "https://api.comdirect.de/oauth/token"
	
	payload = "client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=password&username=" + username + "&password=" + password
	headers = {
	  'Content-Type': 'application/x-www-form-urlencoded',
	  'Accept': 'application/json',
	  'Cookie': cookie
	}
	
	response = requests.request("POST", url, headers=headers, data=payload).json()
	
	return response


def guid():
    def _p8(s):
        p = uuid.uuid4().hex
        return f"-{p[:4]}-{p[4:8]}" if s else p[:8]
    return _p8(False) + _p8(True) + _p8(True) + _p8(False)


def request():
	return str(time.time_ns() // 1_000_000)[-9:]
	
	
def validation(identifier,access_token,guid_var,request_var,cookie):
	
	url = "https://api.comdirect.de/api/session/clients/user/v1/sessions/" + identifier + "/validate"
	
	payload = json.dumps({
	  "identifier": "" + identifier + "",
	  "sessionTanActive": True,
	  "activated2FA": True
	})
	headers = {
	  'Accept': 'application/json',
	  'Authorization': 'Bearer ' + access_token + '',
	  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
	  'Content-Type': 'application/json',
	  'Cookie': cookie
	}
		
	response = requests.post(url, headers=headers, data=payload)
	
	input("Taste drücken um TAN Freigabe zu bestätigen...")
	
	# return ID
	return response.headers['x-once-authentication-info'][7:16]

def refresh(client_id,client_secret,refresh_token):
	
	url = "https://api.comdirect.de/oauth/token"
    
	payload = "client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=refresh_token&refresh_token=" + refresh_token
	headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    }
    
	response = requests.request("POST", url, headers=headers, data=payload)
    
	return response
	
	
def activate(identifier,access_token,guid_var,request_var, vali_ID,cookie):
	
	url = "https://api.comdirect.de/api/session/clients/user/v1/sessions/"+ identifier + ""
	
	payload = json.dumps({
	  "identifier": "" + identifier + "",
	  "sessionTanActive": True,
	  "activated2FA": True
	})
	headers = {
	  'Accept': 'application/json',
	  'Authorization': 'Bearer ' + access_token + '',
	  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
	  'Content-Type': 'application/json',
	  'x-once-authentication-info': '{"id":"' + vali_ID + '"}',
	  'x-once-authentication': '000000',
	  'Cookie': cookie
	}
	
	response = requests.request("PATCH", url, headers=headers, data=payload).json()
	return response["identifier"]


def auth_secondary(client_id,client_secret,access_token,cookie):
	
	url = "https://api.comdirect.de/oauth/token"
	
	payload = "client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=cd_secondary&token=" + access_token
	headers = {
	  'Content-Type': 'application/x-www-form-urlencoded',
	  'Accept': 'application/json',
	  'Cookie': cookie
	}
	
	response = requests.request("POST", url, headers=headers, data=payload).json()
	# second access token
	return response
	
def get_depot_ID(access_token,guid_var,request_var,cookie):

	url = "https://api.comdirect.de/api/brokerage/clients/user/v3/depots"

	payload = {}
	headers = {
	  'Accept': 'application/json',
	  'Authorization': 'Bearer ' + access_token + '',
	  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
	  'Content-Type': 'application/json',
	  'Cookie': cookie
	}

	response = requests.request("GET", url, headers=headers, data=payload).json()
	print("Depot: " + response["values"][0]["depotDisplayId"] + " | " + response["values"][0]["depotType"])
	
	return response["values"][0]["depotId"]



def get_depot(depotUUID,access_token,guid_var,request_var,cookie):

	url_account_info = "https://api.comdirect.de/api/banking/clients/user/v2/accounts/balances"
	url = "https://api.comdirect.de/api/brokerage/v3/depots/" + depotUUID + "/positions"
	
	payload = {}
	headers = {
	  'Accept': 'application/json',
	  'Authorization': 'Bearer ' + access_token + '',
	  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
	  'Content-Type': 'application/json',
	  'Cookie': cookie
	}
	
	response = requests.request("GET", url, headers=headers, data=payload).json()
	
	change = response["aggregated"]["profitLossPrevDayAbs"]["value"]
	unit = response["aggregated"]["profitLossPrevDayAbs"]["unit"]
	rel = response["aggregated"]["profitLossPrevDayRel"]
	print('Depoveränderung heute: ' + change + ' ' + unit + ' (' + rel + ' %)')
	
	response_accounts = requests.request("GET", url_account_info, headers=headers, data=payload).json()
	for i in range(3):
		name = response_accounts['values'][i]['account']['accountType']['text']
		value = response_accounts['values'][i]['balance']['value']
		unit = response_accounts['values'][i]['balance']['unit']
		ausgabe = '{} {} {}'.format(name,value,unit)
		print(ausgabe)
	
	return 1
	
	
def body(depotUUID,wkn,type,amount):

	order_body = {
	    "depotId" : depotUUID,
	    "side" : type,
	    "instrumentId" : wkn,
	    "orderType" : "MARKET",
	    "quantity" : {"value": amount, "unit": "XXX"},
		# Börse Stuttgart
	    "venueId" : "FA5644CBF2914EB792FEE82433789013",
	    "validityType" : "GFD"
		}
	
	return order_body



def post_validation(url,order_body,access_token,guid_var,request_var,cookie,i):

	payload = json.dumps(order_body)
	
	headers = {
		  'Accept': 'application/json',
		  'Authorization': 'Bearer ' + access_token + '',
		  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
		  'Content-Type': 'application/json',
		  'Cookie': cookie
		}

	if url == "https://api.comdirect.de/api/brokerage/v3/orders/validation":
		response = requests.post(url, headers=headers, data=payload)

		if (order_body["side"] == "BUY") and (i == 1):
			print(response.headers['X-Http-Response-Info'])
		
		response = response.headers['x-once-authentication-info'][7:16]
	else:
		response = requests.request("POST", url, headers=headers, data=payload).json()
	
	return response


def post_order(order_body,access_token,guid_var,request_var,vali_ID,cookie):

	url = "https://api.comdirect.de/api/brokerage/v3/orders"
	
	payload = json.dumps(order_body)
	headers = {
	  'Accept': 'application/json',
	  'Authorization': 'Bearer ' + access_token + '',
	  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
	  'Content-Type': 'application/json',
	  'x-once-authentication-info': '{"id":"' + vali_ID + '"}',
	  'x-once-authentication': 'TAN_FREI',
	  'Cookie': cookie
	}
	
	response = requests.request("POST", url, headers=headers, data=payload).json()
	
	return response

def get_order_status(order_ID,access_token,guid_var,request_var,cookie):

	url = "https://api.comdirect.de/api/brokerage/v3/orders/" + order_ID

	payload = {}
	headers = {
		  'Accept': 'application/json',
		  'Authorization': 'Bearer ' + access_token + '',
		  'x-http-request-info': '{"clientRequestId":{"sessionId":"' + guid_var + '","requestId":"' + request_var + '" }}',
		  'Content-Type': 'application/json',
		  'Cookie': cookie
		}
	
	response = requests.request("GET", url, headers=headers, data=payload).json()
	
	return response

def make_order(order_body,access_token,guid_var,request_var,vali_ID,cookie,i):

	validation_urls = ["https://api.comdirect.de/api/brokerage/v3/orders/prevalidation","https://api.comdirect.de/api/brokerage/v3/orders/validation", "https://api.comdirect.de/api/brokerage/v3/orders/costindicationexante"]

	for url in validation_urls:
		vali = post_validation(url,order_body,access_token,guid_var,request_var,cookie,i)
		# neue validation ID zum ausführen einer Order
		if url == "https://api.comdirect.de/api/brokerage/v3/orders/validation":
			vali_ID = vali
		if url == "https://api.comdirect.de/api/brokerage/v3/orders/costindicationexante":
			print("name: " + vali["values"][0]["name"])
			print("expectedValue: " + vali["values"][0]["expectedValue"]["value"] + " " + vali["values"][0]["expectedValue"]["unit"])
			print("venueName: " + vali["values"][0]["venueName"])
			if (order_body["side"] == "BUY"):
				print("Kosten des Wertpapierkaufes: " + vali["values"][0]["purchaseCosts"]["sum"]["value"] + " " + vali["values"][0]["purchaseCosts"]["sum"]["unit"])
				if(i == 1):
					input("Taste drücken um loszulegen...")
			else:
				print("Kosten des Wertpapierverkaufes: " + vali["values"][0]["totalCostsAbs"]["value"] + " " + vali["values"][0]["totalCostsAbs"]["unit"])
	
	order_return = post_order(order_body,access_token,guid_var,request_var,vali_ID,cookie)
	order_ID = order_return["orderId"]
	print("Ordertype: " + order_body["side"])
	print("creationTimestamp: " + order_return["creationTimestamp"])
 
	order_status = get_order_status(order_ID,access_token,guid_var,request_var,cookie)
	while order_status["orderStatus"] != 'EXECUTED':
		print("orderStatus: " + order_status["orderStatus"])
		order_status = get_order_status(order_ID,access_token,guid_var,request_var,cookie)
	
	print("executionTimestamp: " + order_status["executions"][0]["executionTimestamp"])
	print("executionPrice: " + str(int(order_status["executions"][0]["executedQuantity"]["value"]) * float(order_status["executions"][0]["executionPrice"]["value"])))
	
	return 1



# read config file
config = configparser.ConfigParser()
config.read("config.ini")
client_id = config.get('credentials','client_id')
client_secret = config.get('credentials','client_secret')
username = config.get('credentials','username')
password = config.get('credentials','password')
wkn = config.get('DEFAULT','wkn')
amount = config.get('DEFAULT','amount')
trades = int(config.get('DEFAULT','trades'))

# create cookie
cookie = get_cookie()

access_token = auth(client_id,client_secret,username,password,cookie)["access_token"]
guid_var = guid()
request_var = request()
identifier = check_status(access_token,guid_var,request_var,cookie)[0]["identifier"]
vali_ID = validation(identifier,access_token,guid_var,request_var,cookie)
identifier = activate(identifier,access_token,guid_var,request_var,vali_ID,cookie)

access_token = auth_secondary(client_id,client_secret,access_token,cookie)["access_token"]
refresh_token = auth_secondary(client_id,client_secret,access_token,cookie)["refresh_token"]

# get depot ID
depotUUID = get_depot_ID(access_token,guid_var,request_var,cookie)
print("Hier deine Info:")
get_depot(depotUUID,access_token,guid_var,request_var,cookie)

i = 1
while i <= trades:
    
    print("Trade: " + str(i))
    order_body = body(depotUUID,wkn,"BUY",amount)
    make_order(order_body,access_token,guid_var,request_var,vali_ID,cookie,i)
    order_body = body(depotUUID,wkn,"SELL",amount)
    make_order(order_body,access_token,guid_var,request_var,vali_ID,cookie,i)
    i = i + 1
    print("-------------------------------------------")
    
    # session expires in 10 minutes
    #refresh_re = refresh(client_id,client_secret,refresh_token).json()
    
    #access_token = refresh_re["access_token"]
    #refresh_token = refresh_re["refresh_token"]
    
    #get_depot(depotUUID,access_token,guid_var,request_var,cookie)