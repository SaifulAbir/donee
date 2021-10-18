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


def payment(token, id):
    headers = {"Content-Type": "application/json", "Authorization": 'Bearer ' + token}
    url = "https://api.sandbox.paypal.com/v2/checkout/orders/{0}".format(id)

    result = requests.get(url, headers=headers)
    return result.json()