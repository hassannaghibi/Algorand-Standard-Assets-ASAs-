# Algorand-Standard-Assets-ASAs with third party API services (Python)
**Algorand Standard Assets (ASAs)**

The Algorand protocol supports the creation of on-chain assets that benefit from the same security, compatibility, speed and ease of use as the Algo. The official name for assets on Algorand is Algorand Standard Assets (ASA).

With Algorand Standard Assets you can represent stablecoins, loyalty points, system credits, and in-game points, just to name a few examples. You can also represent single, unique assets like a deed for a house, collectable items, unique parts on a supply chain, etc. There is also optional functionality to place transfer restrictions on an asset that help support securities, compliance, and certification use cases.

Use third-party API services to access native Algorand REST APIs for the mainnet, testnet, and betanet. This is an excellent choice if you don't want to set up a local network using Docker, and just want to experiment with Algorand development initially. Existing service providers are Purestake and Rand Labs. Bear in mind that the free tiers for both service providers come with certain limitations, like the number of requests per second (more information on both websites). You can access these services via an API key and Algorand node address.

refrences : 
 - https://developer.algorand.org/docs/get-started/devenv/
 - https://developer.algorand.org/docs/get-details/asa/
 - 

## Required PyPi Libs
- **py-algorand-sdk 1.9.0**
A python library for interacting with the Algorand network.
```
pip install py-algorand-sdk
```

## How to Run Script
**for using the code you just enter you required information of your token into the function `create_token_algo`:**
```
create_token_algo(
    "https://testnet-algorand.api.purestake.io/ps2",    # network address mainnet or testnet
    "", 
    "13yXjVeCPBhNYQtKexAGbC4XjVeCP80dD4Fx1utU8", # your-api-key-from-Purestake-or-RandLabs
    "myself world ocean squirrel myself myself prison sniff myself surface prefer three text myself river joy myself monster useful myself emerge mammal duty myself royal", # creator Seed phrase wallet
    "world ocean myself ocean myself myself prison world myself surface prefer three text myself river world myself monster useful myself emerge mammal duty myself world", # manager Seed phrase wallet
    1000000, # number of your token
    "ALGO", # YOUR-TOKEN-NAME
    "algo", # your-token-name
    "https://path/to/your/asset/details", # your token website url
    8   # integer number of decimals for asset unit calculation 
)
```

## Functions
**wait_for_confirmation**
```
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
```
**print_created_asset**
```
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
```
**print_asset_holding**
```
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
```
**create_token_algo**
```
def create_token_algo(algod_address,algod_token,api_key, creator_mnemonic_phrase, manager_mnemonic_phrase, total, unit_name, asset_name, url, decimals):
    # Setup HTTP client w/guest key provided by PureStake
    headers = {
        "X-API-Key": api_key,
    }

    #creator
    creator_private_key = mnemonic.to_private_key(creator_mnemonic_phrase)
    creator_public_key = mnemonic.to_public_key(creator_mnemonic_phrase)  
    
    #manager
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
```
