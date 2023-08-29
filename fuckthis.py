import requests
import urllib.parse

API_KEY="tye9nlckI16De5xpQTfXrffPds4MdIBN"
#INITIAL_URL="https://api.ecobee.com/authorize?response_type=ecobeePin&client_id="
TOKEN_URL="https://api.ecobee.com/token"
REFRESH_TOKEN="cDsItglAJpAdHBKgfCNdawWiMzj2gKGniInUHtijkXgYk"


#getting_auth_code_url = INITIAL_URL+API_KEY+"&scope=smartWrite"
#resp = requests.get(getting_auth_code_url)

#AUTH_CODE=resp.json()["code"]
#print(AUTH_CODE)

#data = {"grant_type":"ecobeePin", "code":AUTH_CODE,"client_id":API_KEY}
#exit()

data = {"grant_type":"refresh_token", "code":REFRESH_TOKEN, "client_id":API_KEY}

resp = requests.post(TOKEN_URL, data=data)
print(resp)

access_token = resp.json()["access_token"]
REFRESH_TOKEN =  resp.json()["refresh_token"]

print("access", access_token, "refresh", REFRESH_TOKEN)

HEADERS = {"Content-Type": "text/json", "Authorization": 'Bearer {}'.format(access_token)}
#print(urllib.parse.urlencode body.json())

body ={"selection":{"selectionType":"registered","selectionMatch":"","includeRuntime":True}} 

resp = requests.get('https://api.ecobee.com/1/thermostat?format=json&body={"selection":{"selectionType":"registered","selectionMatch":"","includeRuntime":true}}', headers = HEADERS)
print(resp)
print(resp.text)
#curl -s -format=json&body=\
