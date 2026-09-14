'''
Plaid connection definition
'''
from plaid.api import plaid_api
import plaid
import json
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.item_public_token_exchange_request import (ItemPublicTokenExchangeRequest)
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest
)
from plaid.model.sandbox_public_token_create_request_options import (SandboxPublicTokenCreateRequestOptions)
from dotenv import load_dotenv, set_key
import os
import keyring

load_dotenv(override=True)

def save_state():
    json.dumps()

client_id = os.getenv('PLAID_CLIENT_ID')
client_secret = os.getenv('PLAID_CLIENT_SECRET')
access_token = os.getenv('PLAID_ACCESS_TOKEN')
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId':client_id,
        'secret': client_secret
    }
)

api_client = plaid.ApiClient(configuration) # Lower level http
client = plaid_api.PlaidApi(api_client) # plaid-specific interface
sandbox_options = SandboxPublicTokenCreateRequestOptions(
    override_username="user_transactions_dynamic",
    override_password="pass_good"
)
# request = SandboxPublicTokenCreateRequest(
#     institution_id="ins_109508",
#     initial_products=[Products("transactions")], 
#     options=sandbox_options
# )

# response = client.sandbox_public_token_create(request)
# public_token = response["public_token"]

# exchange_request = ItemPublicTokenExchangeRequest(
#     public_token=public_token
# )

# exchange_response = client.item_public_token_exchange(exchange_request)
# access_token = exchange_response['access_token']
# print(access_token)

transaction_request = TransactionsSyncRequest(
    access_token=access_token
)

response = client.transactions_sync(transaction_request)
print(response)
transactions = []
cursor = response['next_cursor']

while (response['has_more']):
    request = TransactionsSyncRequest(
        access_token = access_token,
        cursor=cursor
    )
    response = client.transactions_sync(request)
    transactions += response['added']
save_plaid_state({'PLAID_CURSOR':response['next_cursor']})
# save_plaid_state({'CURSOR':'tester'})

