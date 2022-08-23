from application import application as app
import pytest
from flask.testing import FlaskClient

@pytest.fixture
def client():
    return app.test_client()

def test_route(client: FlaskClient):
    """should be a successful GET request"""
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json.get('message', 'Hello world! Testing!!!!!!!!!!')

def test_upload_users(client: FlaskClient):
    """user file should be uploaded"""
    url = '/user/upload'
    files ={
        "file" : (open('test data/users.csv','rb'),'users.csv')
        }
    resp = client.post(url,data=files)
    assert resp.status_code == 200
    assert resp.get_data("Successfully updated 9 card records and 4 user records")

def test_get_card_by_user_id_1(client: FlaskClient):
    """should return first user's card info"""
    url = '/card/get_by_user_id'
    user_id = '398b9697-9e1f-4289-8db5-7918abf38d28'
    data = {
        'user_id': user_id
    }
    resp = client.post(url,data = data)
    assert resp.status_code == 200
    # records = resp.get_json()
    # assert len(records)==3
    # assert records[0]== '5ed2aa6f-4644-4882-8d00-a290581d8e37'
    # assert records[1]== '398b9697-9e1f-4289-8db5-7918abf38d28'
    # assert records[2]== 'scis_platinummiles'
    # assert records[3]== '0.000'

def test_get_card_by_user_id_2(client: FlaskClient):
    """should return second user's card info"""
    url = '/card/get_by_user_id'
    user_id = '4c96e1df-4f1b-4f40-9930-d521db013c0d'
    data = {
        'user_id': user_id
    }
    resp = client.post(url,data = data)
    assert resp.status_code == 200
    # records = resp.get_json()
    # assert len(records)==3

def test_get_card_by_user_id_3(client: FlaskClient):
    """should return third user's card info"""
    url = '/card/get_by_user_id'
    user_id = '2ee568eb-9293-4d9c-8c5b-ab312d4a1ba0'
    data = {
        'user_id': user_id
    }
    resp = client.post(url,data = data)
    assert resp.status_code == 200
    # records = resp.get_json()
    # assert len(records)==3

def test_get_card_by_user_id_4(client: FlaskClient):
    """should return fourth user's card info"""
    url = '/card/get_by_user_id'
    user_id = '6b548a95-4b65-4c56-8e3e-674bb5aca20b'
    data = {
        'user_id': user_id
    }
    resp = client.post(url,data = data)
    assert resp.status_code == 200
    # records = resp.get_json()
    # assert len(records)==3

def test_add_default_campaigns(client: FlaskClient):
    """should add all default campaigns"""
    url = '/campaigns/add_default_campaigns'
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.get_data("Successfully Added Default Campaigns")

# def test_view_default_campaigns(client: FlaskClient):
#     """should return list of default campaigns"""
#     url = '/client/view_campaigns'
#     resp = client.get(url)
#     assert resp.status_code == 200
    
def test_add_campaigns(client: FlaskClient):
    """should add new capaign"""
    url = '/campaigns/add_campaigns'
    new_campaign = [
        {
            'campaign_id': 5,
            'card_type': 'SCIS Travel Card',
            'campaign_desc': '5 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        }]

    resp = client.post(url,data = {'campaigns':new_campaign})
    assert resp.status_code == 200
    # assert resp.get_data() == b"Successfully Added New Campaigns"
    
# def test_view_added_campaigns(client: FlaskClient)

def test_upload_transactions(client: FlaskClient):
    """transaction file should be uploaded"""
    url = '/transaction/upload'
    files ={
        "file" : (open('test data/spend.csv','rb'),'spend.csv')
        }
    resp = client.post(url,data=files)
    assert resp.status_code == 200
    assert resp.get_data("(Successfully updated 478602 records)")

def test_get_transaction(client: FlaskClient):
    """should return transaction records"""
    page = {'page_size': 3,
            'page_number': 1}
    url = '/transaction/get'
    resp = client.post(url,data=page)
    assert resp.status_code == 200
    # output = resp.get_json()
    # assert len(output) == 3

def test_add_new_campaigns(client: FlaskClient):
    """should add new capaign"""
    url = '/campaigns/add_campaigns'
    new_campaign = [
        {
            'campaign_id': 6,
            'card_type': 'HSBC Travel Card',
            'campaign_desc': '5 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        }]

    resp = client.post(url,data = {'campaigns':new_campaign})
    assert resp.status_code == 200

def test_add_new_campaigns_2(client: FlaskClient):
    """should add new capaign"""
    url = '/campaigns/add_campaigns'
    new_campaign = [
        {
            'campaign_id': 7,
            'card_type': 'HSBC shopping Card',
            'campaign_desc': '5 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        }]

    resp = client.post(url,data = {'campaigns':new_campaign})
    assert resp.status_code == 200

def test_add_list_campaigns(client: FlaskClient):
    """should add new capaign"""
    url = '/campaigns/add_campaigns'
    new_campaign = [
        {
            'campaign_id': 8,
            'card_type': 'HSBC shopping Card',
            'campaign_desc': '5 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        },
        {
            'campaign_id': 9,
            'card_type': 'DBS shopping Card',
            'campaign_desc': '5 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        },
        {
            'campaign_id': 8,
            'card_type': 'DBS Travel Card',
            'campaign_desc': '5 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        }]

    resp = client.post(url,data = {'campaigns':new_campaign})
    assert resp.status_code == 200

def test_get_transaction(client: FlaskClient):
    """should return transaction records"""
    page = {'page_size': 6,
            'page_number': 3}
    url = '/transaction/get'
    resp = client.post(url,data=page)
    assert resp.status_code == 200
    output = resp.get_json()
    # assert len(output) == 3

# def test_get_rewards_by_user_id(client: FlaskClient):
#     url = '/user/get_reward_by_user_id'
#     user_id = "398b9697-9e1f-4289-8db5-7918abf38d28"
#     resp = client.post(url,data={'user_id':user_id})
#     assert resp.status_code == 200
#     output = resp.get_json()
#     # assert len(output) == 3
#     assert output['points'] == 0

# def test_get_rewards_by_user_id_2(client: FlaskClient):
#     url = '/user/get_reward_by_user_id'
#     user_id = "2ee568eb-9293-4d9c-8c5b-ab312d4a1ba0"
#     resp = client.post(url,data={'user_id':user_id})
#     assert resp.status_code == 200
#     output = resp.get_json()
#     # assert len(output) == 3
#     assert output['points'] == 0

# def test_get_rewards_by_user_id_3(client: FlaskClient):
#     url = '/user/get_reward_by_user_id'
#     user_id = "4c96e1df-4f1b-4f40-9930-d521db013c0d"
#     resp = client.post(url,data={'user_id':user_id})
#     assert resp.status_code == 200
#     output = resp.get_json()
#     # assert len(output) == 3
#     assert output['points'] == 0

# def test_get_rewards_by_user_id_4(client: FlaskClient):
#     url = '/user/get_reward_by_user_id'
#     user_id = "6b548a95-4b65-4c56-8e3e-674bb5aca20b"
#     resp = client.post(url,data={'user_id':user_id})
#     assert resp.status_code == 200
#     output = resp.get_json()
#     # assert len(output) == 3
#     assert output['points'] == 0

def test_add_new_transaction(client: FlaskClient):
    """should add new transaction"""
    new_transaction = {
        "transactions": [
            {
                "transaction_id": "c431cdc83abf302a55ba904426abdfa198ac18bbcfa1455cb9de5b2f351886d0", 
                "transaction_date": "2021-08-27",
                "amount": 279.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516",
                "card_type": "scis_premiummiles"
            }
        ]
    }
    url = '/transaction/add'
    resp = client.post(url,data=new_transaction)
    assert resp.status_code == 200
    assert resp.get_data("Successfully added records")

def test_add_new_transaction_1(client: FlaskClient):
    """should add new transaction"""
    new_transaction = {
        "transactions": [
            {
                "transaction_id": "c431cdc83abf302a55ba904426abdfa198ac18bbcfa1455cb9de5b2f3512346d0", 
                "transaction_date": "2021-08-27",
                "amount": 279.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516",
                "card_type": "scis_premiummiles"
            }
        ]
    }
    url = '/transaction/add'
    resp = client.post(url,data=new_transaction)
    assert resp.status_code == 200
    assert resp.get_data("Successfully added records")

def test_add_new_transaction_2(client: FlaskClient):
    """should add new transaction"""
    new_transaction = {
        "transactions": [
            {
                "transaction_id": "c431cdc83abf302a55ba904426abdfel38ac18bbcfa1455cb9de5b2f3512346d0", 
                "transaction_date": "2021-08-27",
                "amount": 979.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516",
                "card_type": "scis_premiummiles"
            }
        ]
    }
    url = '/transaction/add'
    resp = client.post(url,data=new_transaction)
    assert resp.status_code == 200
    assert resp.get_data("Successfully added records")

def test_add_new_list_transaction(client: FlaskClient):
    """should add new transaction"""
    new_transaction = {
        "transactions": [
            {
                "transaction_id": "c431cdc83abf302a55ba904dksabdfa198ac18bbcfa1455cb9de5b2f3512346d0", 
                "transaction_date": "2021-08-27",
                "amount": 279.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516",
                "card_type": "scis_premiummiles"
            },
            {
                "transaction_id": "c431cdc83abf302a55blsk4426abdfa198ac18bbcfa1455cb9de5b2f3512346d0", 
                "transaction_date": "2021-08-27",
                "amount": 983.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516",
                "card_type": "scis_premiummiles"
            },
            {
                "transaction_id": "c431cdc83abf302a55dls04426abdfa198ac18bbcfa1455cb9de5b2f3512346d0", 
                "transaction_date": "2021-08-27",
                "amount": 498.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516",
                "card_type": "scis_premiummiles"
            }
        ]
    }
    url = '/transaction/add'
    resp = client.post(url,data=new_transaction)
    assert resp.status_code == 200
    assert resp.get_data("Successfully added records")

def test_get_new_transaction_after_add(client: FlaskClient):
    """should return transaction records"""
    page = {'page_size': 3,
            'page_number': 1}
    url = '/transaction/get'
    resp = client.post(url,data=page)
    assert resp.status_code == 200
    output = resp.get_json()
    # assert len(output) == 3
    
def test_get_new_individual_rewards_by_user_id_after_add(client: FlaskClient):
    url = "/transaction/rewardpoint"
    client_id = '383a8d8e-9cb7-454f-83d9-45e3995ee4ce'
    resp = client.post(url, data = {'user_id':client_id})
    assert resp.status_code == 200

# def test_get_new_rewards_by_user_id_after_add(client: FlaskClient):
#     """should return the user's rewards"""
#     url = '/user/get_reward_by_user_id'
#     user_id = "4c96e1df-4f1b-4f40-9930-d521db013c0d"
#     resp = client.post(url,data={'user_id':user_id})
#     assert resp.status_code == 200
#     output = resp.get_json()
#     # assert len(output) == 3
#     assert output['points'] == 0
# testing!!!!!

# def test_get_transaction_by_user_id(client: FlaskClient):
#     url = '/transaction/get_by_user_id'
#     user_id = "398b9697-9e1f-4289-8db5-7918abf38d28"
#     resp = client.post(url,data={'user_id':user_id})
#     assert resp.status_code == 200
#     output = resp.get_json()
#     assert len(output) == 3

# def test_get_individual_rewards_by_user_id(client: FlaskClient)
# def test_get_rewards_by_user_id(client: FlaskClient)

# def test_add_transaction(client: FlaskClient)
# def test_get_transaction_after_add(client: FlaskClient)
# def test_get_transaction_by_user_id_after_add(client: FlaskClient)
# def test_get_individual_rewards_by_user_id_after_add(client: FlaskClient)
# def test_get_rewards_by_user_id_after_add(client: FlaskClient)

