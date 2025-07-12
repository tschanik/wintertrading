import configparser
import requests
import json
import uuid
import time
from datetime import datetime

class ComdirectAPI:
    def __init__(self, client_id, client_secret, username, password):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json', 'Content-Type': 'application/json'})
        self.access_token = None
        self.refresh_token = None
        self.guid_var = self.guid()
        self.request_var = self.request()
        self.cookie = self.get_cookie()
        self.session.headers.update({'Cookie': self.cookie})

    def _request(self, method, url, **kwargs):
        headers = kwargs.get('headers', {})
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        headers['x-http-request-info'] = f'{{"clientRequestId":{{"sessionId":"{self.guid_var}","requestId":"{self.request_var}"}}}}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_cookie(self):
        session_id = uuid.uuid4().hex
        return f"qSession={session_id}"

    def check_status(self):
        url = "https://api.comdirect.de/api/session/clients/user/v1/sessions"
        response = self._request("GET", url)
        return response.json()

    def auth(self):
        url = "https://api.comdirect.de/oauth/token"
        payload = f"client_id={self.client_id}&client_secret={self.client_secret}&grant_type=password&username={self.username}&password={self.password}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = self._request("POST", url, headers=headers, data=payload)
        data = response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        return data

    def guid(self):
        def _p8(s):
            p = uuid.uuid4().hex
            return f"-{p[:4]}-{p[4:8]}" if s else p[:8]
        return _p8(False) + _p8(True) + _p8(True) + _p8(False)

    def request(self):
        return str(time.time_ns() // 1_000_000)[-9:]

    def validation(self, identifier):
        url = f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{identifier}/validate"
        payload = json.dumps({
            "identifier": identifier,
            "sessionTanActive": True,
            "activated2FA": True
        })
        response = self._request("POST", url, data=payload)
        input("Taste drücken um TAN Freigabe zu bestätigen...")
        return response.headers['x-once-authentication-info'][7:16]

    def refresh(self):
        url = "https://api.comdirect.de/oauth/token"
        payload = f"client_id={self.client_id}&client_secret={self.client_secret}&grant_type=refresh_token&refresh_token={self.refresh_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = self._request("POST", url, headers=headers, data=payload)
        data = response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        return data

    def activate(self, identifier, vali_ID):
        url = f"https://api.comdirect.de/api/session/clients/user/v1/sessions/{identifier}"
        payload = json.dumps({
            "identifier": identifier,
            "sessionTanActive": True,
            "activated2FA": True
        })
        headers = {
            'x-once-authentication-info': f'{{"id":"{vali_ID}"}}',
            'x-once-authentication': '000000'
        }
        response = self._request("PATCH", url, headers=headers, data=payload)
        return response.json()["identifier"]

    def auth_secondary(self):
        url = "https://api.comdirect.de/oauth/token"
        payload = f"client_id={self.client_id}&client_secret={self.client_secret}&grant_type=cd_secondary&token={self.access_token}"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = self._request("POST", url, headers=headers, data=payload)
        data = response.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        return data

    def get_depot_ID(self):
        url = "https://api.comdirect.de/api/brokerage/clients/user/v3/depots"
        response = self._request("GET", url)
        data = response.json()
        print(f"Depot: {data['values'][0]['depotDisplayId']} | {data['values'][0]['depotType']}")
        return data['values'][0]['depotId']

    def get_depot(self, depotUUID):
        url_account_info = "https://api.comdirect.de/api/banking/clients/user/v2/accounts/balances"
        url = f"https://api.comdirect.de/api/brokerage/v3/depots/{depotUUID}/positions"
        
        response = self._request("GET", url)
        data = response.json()

        for item in data['values']:
            wkn = item["wkn"]
            wkn_info_url = f"https://api.comdirect.de/api/brokerage/v1/instruments/{wkn}"
            wkn_info = self._request("GET", wkn_info_url).json()
            
            name = wkn_info["values"][0]["name"]
            short_name = wkn_info["values"][0]["shortName"]
            sector = wkn_info["values"][0]["staticData"].get("sector", "")
            instrument_type = wkn_info["values"][0]["staticData"]["instrumentType"]
            amount = float(item["quantity"]["value"])
            current_value = float(item["currentValue"]["value"])
            unit = item["currentValue"]["unit"]
            profit_loss = float(item["profitLossPurchaseAbs"]["value"])
            profit_loss_rel = float(item["profitLossPurchaseRel"])
            sell_possible = item["sellPossible"]

            profit_loss_color = "\u001b[92m" if profit_loss >= 0 else "\u001b[91m"
            reset_color = "\u001b[0m"
            sell_status = "✅ Ja" if sell_possible else "❌ Nein"

            print(f"--- Wertpapier: {short_name} ---")
            print(f"  WKN: {wkn}")
            print(f"  Typ: {instrument_type}")
            print(f"  Sektor: {sector}")
            print(f"  Anzahl: {amount:,.2f}")
            print(f"  Aktueller Wert: {current_value:,.2f} {unit}")
            print(f"  Entwicklung (Absolut): {profit_loss_color}{profit_loss:,.2f} {unit}{reset_color}")
            print(f"  Entwicklung (Relativ): {profit_loss_color}{profit_loss_rel:,.2f} %{reset_color}")
            print(f"  Verkaufbar: {sell_status}")
            print("-" * 40 + "\n")

        change = data["aggregated"]["profitLossPrevDayAbs"]["value"]
        unit = data["aggregated"]["profitLossPrevDayAbs"]["unit"]
        rel = data["aggregated"]["profitLossPrevDayRel"]
        print(f"Depoveränderung heute: {change} {unit} ({rel} %)")

        response_accounts = self._request("GET", url_account_info).json()
        for acc in response_accounts['values']:
            name = acc['account']['accountType']['text']
            value = acc['balance']['value']
            unit = acc['balance']['unit']
            print(f"{name} {value} {unit}")

    def body(self, depotUUID, wkn, type, amount):
        return {
            "depotId": depotUUID,
            "side": type,
            "instrumentId": wkn,
            "orderType": "MARKET",
            "quantity": {"value": amount, "unit": "XXX"},
            "venueId": "FA5644CBF2914EB792FEE82433789013",
            "validityType": "GFD"
        }

    def post_validation(self, url, order_body, i):
        payload = json.dumps(order_body)
        response = self._request("POST", url, data=payload)

        if url == "https://api.comdirect.de/api/brokerage/v3/orders/validation":
            if order_body["side"] == "BUY" and i == 1:
                try:
                    print(response.headers['X-Http-Response-Info'])
                except KeyError:
                    print('X-Http-Response-Info is empty')
            return response.headers['x-once-authentication-info'][7:16]
        else:
            return response.json()

    def post_order(self, order_body, vali_ID):
        url = "https://api.comdirect.de/api/brokerage/v3/orders"
        payload = json.dumps(order_body)
        headers = {
            'x-once-authentication-info': f'{{"id":"{vali_ID}"}}',
            'x-once-authentication': 'TAN_FREI'
        }
        response = self._request("POST", url, headers=headers, data=payload)
        return response.json()

    def get_order_status(self, order_ID):
        url = f"https://api.comdirect.de/api/brokerage/v3/orders/{order_ID}"
        response = self._request("GET", url)
        return response.json()

    def make_order(self, order_body, i):
        validation_urls = [
            "https://api.comdirect.de/api/brokerage/v3/orders/prevalidation",
            "https://api.comdirect.de/api/brokerage/v3/orders/validation",
            "https://api.comdirect.de/api/brokerage/v3/orders/costindicationexante"
        ]
        print(f"Ordertype: {order_body['side']}")
        vali_ID = None
        for url in validation_urls:
            vali = self.post_validation(url, order_body, i)
            if url == "https://api.comdirect.de/api/brokerage/v3/orders/validation":
                vali_ID = vali
            if url == "https://api.comdirect.de/api/brokerage/v3/orders/costindicationexante":
                print(f"name: {vali['values'][0]['name']}")
                print(f"expectedValue: {vali['values'][0]['expectedValue']['value']} {vali['values'][0]['expectedValue']['unit']}")
                print(f"venueName: {vali['values'][0]['venueName']}")
                if order_body["side"] == "BUY":
                    print(f"Kosten des Wertpapierkaufes: {vali['values'][0]['purchaseCosts']['sum']['value']} {vali['values'][0]['purchaseCosts']['sum']['unit']}")
                    if i == 1:
                        input("Taste drücken um loszulegen...")
                else:
                    print(f"Kosten des Wertpapierverkaufes: {vali['values'][0]['totalCostsAbs']['value']} {vali['values'][0]['totalCostsAbs']['unit']}")

        order_return = self.post_order(order_body, vali_ID)
        order_ID = order_return["orderId"]
        print(f"creationTimestamp: {order_return['creationTimestamp']}")

        order_status = self.get_order_status(order_ID)
        while order_status["orderStatus"] != 'EXECUTED':
            print(f"orderStatus: {order_status['orderStatus']}")
            time.sleep(1)
            order_status = self.get_order_status(order_ID)

        price = int(order_status["executions"][0]["executedQuantity"]["value"]) * float(order_status["executions"][0]["executionPrice"]["value"])
        print(f"executionTimestamp: {order_status['executions'][0]['executionTimestamp']}")
        print(f"executionPrice: {price}")
        return price

def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    client_id = config.get('credentials', 'client_id')
    client_secret = config.get('credentials', 'client_secret')
    username = config.get('credentials', 'username')
    password = config.get('credentials', 'password')
    wkn = config.get('DEFAULT', 'wkn')
    amount = config.get('DEFAULT', 'amount')
    trades = int(config.get('DEFAULT', 'trades'))

    api = ComdirectAPI(client_id, client_secret, username, password)
    api.auth()
    
    status = api.check_status()
    identifier = status[0]["identifier"]
    
    vali_ID = api.validation(identifier)
    identifier = api.activate(identifier, vali_ID)
    
    api.auth_secondary()

    depotUUID = api.get_depot_ID()
    print("Hier deine Info:")
    api.get_depot(depotUUID)

    delta = 0
    for i in range(1, trades + 1):
        print(f"Trade: {i}")
        order_body_buy = api.body(depotUUID, wkn, "BUY", amount)
        price_buy = api.make_order(order_body_buy, i)
        
        order_body_sell = api.body(depotUUID, wkn, "SELL", amount)
        price_sell = api.make_order(order_body_sell, i)
        
        delta += (price_sell - price_buy)
        print("-------------------------------------------")
        print(f"Gewinn/Verlust: {delta} EUR")
        print("-------------------------------------------")
        
        api.refresh()

if __name__ == "__main__":
    main()
