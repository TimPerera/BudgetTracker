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
import logging
from collections import defaultdict

from database import fetch_cursor

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - LN:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

def save_state():
    json.dumps()

def get_transactions(client, cursor, access_token, page_limit=5):

    transaction_request = TransactionsSyncRequest(
        access_token=access_token, 
        cursor=cursor if cursor else ''
    )
    response = client.transactions_sync(transaction_request)
    transactions = defaultdict(list)
    next_cursor = response['next_cursor']
    more_transactions = response['has_more']
    page_num = 0

    while more_transactions and page_num<=page_limit:
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=next_cursor
        )
        response = client.transactions_sync(request)
        transactions['added'].append(response['added'])
        transactions['removed'].append(response['removed'])
        transactions['modified'].append(response['modified'])
        next_cursor = response['next_cursor']
        page_num += 1
    logger.debug(f'Returned {len(transactions)} transactions.')
    return transactions, next_cursor


def get_access_token(client):
    logger.debug("Getting new access token")
    sandbox_options = SandboxPublicTokenCreateRequestOptions(
    override_username="user_transactions_dynamic",
    override_password="pass_good"
)
    request = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508",
        initial_products=[Products("transactions")], 
        options=sandbox_options
    )

    response = client.sandbox_public_token_create(request)
    public_token = response["public_token"]

    exchange_request = ItemPublicTokenExchangeRequest(
        public_token=public_token
    )

    exchange_response = client.item_public_token_exchange(exchange_request)
    access_token = exchange_response['access_token']
    return access_token

def get_client():
    client_id = os.getenv('PLAID_CLIENT_ID')
    client_secret = os.getenv('PLAID_CLIENT_SECRET')
    configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId':client_id,
            'secret': client_secret
        }
    )
    api_client = plaid.ApiClient(configuration) # Lower level http
    
    client = plaid_api.PlaidApi(api_client) # plaid-specific interface
    return client
    

def main():
    # Get states
    # print(os.getenv('PLAID_ACCESS_TOKEN'))
    
    client = get_client()
    if  not (access_token:= os.getenv('PLAID_ACCESS_TOKEN')):
        access_token = get_access_token(client)
    cursor = fetch_cursor()
    # # Get transactions
    transactions, next_cursor= get_transactions(client, cursor, access_token)
    for t_type, vals in transactions.items():
        logger.debug(f'Transaction Type:{t_type}:{len(vals)} transactions')
    # # Save states
    # pass

if __name__=='__main__':
    main()