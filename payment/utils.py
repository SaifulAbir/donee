import base64
import requests
from Donee.settings import CLIENT_ID, CLIENT_SECRET


def paypal_token():

    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET,
        "grant_type":"client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode())
    }

    token = requests.post(url, data, headers=headers)
    return token.json()


def payment(token, amount):
    headers = {"Content-Type": "application/json", "Authorization": 'Bearer ' + token}
    url = "https://api.sandbox.paypal.com/v2/checkout/orders"
    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": "100.00"
                }
            }
        ]
    }

    result = requests.post(url, headers=headers, json=data)
    return result.json()