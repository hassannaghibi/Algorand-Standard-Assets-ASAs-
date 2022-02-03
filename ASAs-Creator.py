import json
from unicodedata import decimal
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk.future.transaction import AssetConfigTxn

 
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print('Waiting for confirmation')
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print('Transaction confirmed in round', txinfo.get('confirmed-round'))
    return txinfo


def print_created_asset(algodclient, account, assetid):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['index'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break


def print_asset_holding(algodclient, account, assetid):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break


def create_token_algo(algod_address, algod_token, api_key, creator_mnemonic_phrase, manager_mnemonic_phrase, total, unit_name, asset_name, url, decimals):
    # Setup HTTP client w/guest key provided by PureStake
    headers = {
        "X-API-Key": api_key,
    }

    # creator
    creator_private_key = mnemonic.to_private_key(creator_mnemonic_phrase)
    creator_public_key = mnemonic.to_public_key(creator_mnemonic_phrase)

    # manager
    manager_private_key = mnemonic.to_private_key(manager_mnemonic_phrase)
    manager_public_key = mnemonic.to_public_key(manager_mnemonic_phrase)

    algodclient = algod.AlgodClient(algod_token, algod_address, headers)

    # CREATE ASSET
    # Get network params for transactions before every transaction.
    params = algodclient.suggested_params()
    # comment these two lines if you want to use suggested params
    params.fee = 1000
    params.flat_fee = True

    txn = AssetConfigTxn(
        sender=creator_public_key,
        sp=params,
        total=total,
        default_frozen=False,
        unit_name=unit_name,
        asset_name=asset_name,
        manager=manager_public_key,
        reserve=manager_public_key,
        freeze=manager_public_key,
        clawback=manager_public_key,
        url=url,
        decimals=decimals)

    # Sign with secret key of creator
    stxn = txn.sign(creator_private_key)

    # Send the transaction to the network and retrieve the txid.
    txid = algodclient.send_transaction(stxn)
    print(txid)

    # Retrieve the asset ID of the newly created asset by first
    # ensuring that the creation transaction was confirmed,
    # then grabbing the asset id from the transaction.

    # Wait for the transaction to be confirmed
    wait_for_confirmation(algodclient, txid)

    try:
        # Pull account info for the creator
        # account_info = algod_client.account_info(accounts[1]['pk'])
        # get asset_id from tx
        # Get the new asset's information from the creator account
        ptx = algodclient.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        print_created_asset(algodclient, creator_public_key, asset_id)
        print_asset_holding(algodclient, creator_public_key, asset_id)
    except Exception as e:
        print(e)


# Run Script
create_token_algo(
    # network address mainnet or testnet
    "https://testnet-algorand.api.purestake.io/ps2",
    "",
    # your-api-key-from-Purestake-or-RandLabs
    "13yXjVeCPBhNYQtKexAGbC4XjVeCP80dD4Fx1utU8",
    "myself world ocean squirrel myself myself prison sniff myself surface prefer three text myself river joy myself monster useful myself emerge mammal duty myself royal",  # creator Seed phrase wallet
    "world ocean myself ocean myself myself prison world myself surface prefer three text myself river world myself monster useful myself emerge mammal duty myself world",  # manager Seed phrase wallet
    1000000,  # number of your token
    "ALGO",  # YOUR-TOKEN-NAME
    "algo",  # your-token-name
    "https://path/to/your/asset/details",  # your token website url
    8   # integer number of decimals for asset unit calculation
)