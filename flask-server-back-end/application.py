from database_handler import *
import pandas as pd
from flask import Flask, request, json, jsonify
import traceback
import requests
from flask_cors import CORS
application = app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app)

@app.route("/")
def test():
  return jsonify({"message": "Hello world! Testing!!!!!"}), 200




@app.route('/user/upload', methods=['POST'])
def upload_users():
    """
    Uploads card records and user records into AWS Aurora's card and user tables respectively using users.csv file
    Cards and users with duplicated transaction ids will replace the exisiting user
    :param user_file: users.csv file found in https://kaligo.exavault.com/files/users
    :type user_file: File
    :return: success status or error message
    :rtype: str

    """
    print("Preparing dataset")
    used_user_ids = set()
    try:
        df = pd.read_csv(request.files['user_file'])
        card_parameter_sets = []
        user_parameter_sets = []
        for index, row in df.iterrows():
            card_parameters = [
                {'name': 'card_id', 'value': {'stringValue': row['card_id']}},
                {'name': 'user_id', 'value': {'stringValue': row['id']}},
                {'name': 'card_type', 'value': {
                    'stringValue': row['card_type']}}
            ]
            card_parameter_sets.append(card_parameters)
            if row['id'] not in used_user_ids:
                user_parameters = [
                    {'name': 'user_id', 'value': {'stringValue': row['id']}},
                    {'name': 'user_name', 'value': {
                        'stringValue': row['first_name'] + " " + row['last_name']}},
                    # TODO: Generate random password for each user
                    {'name': 'user_password', 'value': {'stringValue': "password1"}}
                ]
                user_parameter_sets.append(user_parameters)
                used_user_ids.add(row['id'])
        # print("Updating user id in transaction table")
        # batch_execute_statement("UPDATE transaction SET user_id=:user_id WHERE card_id=:card_id", card_parameter_sets)
        print("Updating cards data in database")
        batch_execute_statement("INSERT into card\
        (card_id, user_id, card_type, score)\
        VALUES(:card_id, :user_id, :card_type, 0)\
        ON DUPLICATE KEY UPDATE\
        user_id=:user_id, card_type=:card_type\
        ", card_parameter_sets, "CARD")
        print("Uploading users data to database")

        batch_execute_statement(
            "REPLACE into user(user_id, user_name, user_password) VALUES(:user_id, :user_name, :user_password)", user_parameter_sets, "USER")
        return "Successfully updated " + str(len(df.index)) + " card records and " + str(len(used_user_ids)) + " user records"
    except Exception:
        return traceback.format_exc()


def calculate_card_total_spent(card_total_spent, row):
    # Feature 4: Exclusions
    if row["merchant"] in ["GrabPay Top up", "AXS Payments", "EZ-Link"]:
        return
    card_spent = row["amount"]
    if row["currency"] == "USD":
        card_spent = 1.36 * card_spent
    if row['card_id'] in card_total_spent:
        card_total_spent[row['card_id']]["card_spent"] += card_spent
    else:
        card_total_spent[row['card_id']] = dict()
        card_total_spent[row['card_id']]["card_spent"] = card_spent
        card_total_spent[row['card_id']]["card_type"] = row["card_type"]
        card_total_spent[row["card_id"]]["transaction_currency"] = row["currency"]

def update_card_score_databases(card_total_spent):
    # Used to update score column for each card
    card_parameter_sets = []
    for card_id, value_dict in card_total_spent.items():
        card_score = 0
         
        # Feature 1: Earn Processing by Nicolas
        card_score += float(calculate_earn_processing(value_dict)["card_score"])

        card_parameters = [
            {'name': 'card_id', 'value': {'stringValue': card_id}},
            {'name': 'user_id', 'value': {'stringValue': ""}},
            {'name': 'card_type', 'value': {
                'stringValue': value_dict['card_type']}},
            {'name': 'score', 'value': {'doubleValue': card_score}}
        ]
        card_parameter_sets.append(card_parameters)
    batch_execute_statement("INSERT into card\
    (card_id, user_id, card_type, score)\
    VALUES(:card_id, :user_id, :card_type, :score)\
    ON DUPLICATE KEY UPDATE\
    score= score + :score\
    ", card_parameter_sets, "CARD")
    return card_score

# Feature 1: Earn Processing by Nicolas
def calculate_earn_processing(value_dict):
    card_score = 0
    card_type = value_dict["card_type"]
    card_spent = value_dict["card_spent"]
    print(card_spent)
    transaction_currency = value_dict["transaction_currency"]
    card_campaign = ""
    if card_type == "scis_shopping":
        card_score += 1 * card_spent
        card_campaign = "1 point per SGD spent"
    elif card_type == "scis_premiummiles":
        card_score += 1.1 * card_spent
        card_campaign = "1.1 miles per SGD"
        if transaction_currency != "SGD":
            card_score += 2.2 * card_spent
            card_campaign = "2.2 miles per SGD on foreign card spent"
    elif card_type == "scis_platinummiles":
        if transaction_currency == "SGD":
            card_score += 1.4 * card_spent
            card_campaign = "1.4 miles per SGD"
        elif transaction_currency != "SGD":
            card_score += 3 * card_spent
            card_campaign = "3 miles per SGD on foreign card spent"
    elif card_type == "scis_freedom":
        card_score += 0.005 * card_spent
        card_campaign = "0.5% cashback on all spent"
        if card_spent > 500 and transaction_currency == "SGD":
            card_score += 0.01 * card_spent
            card_campaign = "1% cashback for all spent >SGD 500"
        elif card_spent > 2000 and transaction_currency == "SGD":
            card_score += 0.03 * card_spent
            card_campaign = "3% cashback for all spent >SGD 2000"
    earn_processing = dict()
    earn_processing["card_score"] = card_score
    earn_processing["card_campaign"] = card_campaign
    return earn_processing


@app.route("/transaction/rewardpoint", methods=['POST'])
def get_individual_rewards_by_user_id():
    try:
        request_data = request.get_json(force=True)
        user_id = request_data["user_id"]
        if user_id == "":
            return '[]'

        sql_find_user_card = "SELECT * FROM card WHERE user_id = '" + user_id + "'"
        print(sql_find_user_card)
        json_user_card_response = execute_statement(sql_find_user_card)

        data_individual_rewards_by_user_id_list = []
        if len(json_user_card_response["records"]) > 0:
            card_type = json_user_card_response["records"][0][2]["stringValue"]
            card_id = json_user_card_response["records"][0][0]["stringValue"]

            sql_find_card_transaction = "SELECT * FROM transaction WHERE card_id = '" + card_id + "'"
            page_size = int(request_data['page_size'])
            page_number = int(request_data['page_number'])
            limit = page_size
            offset = (page_size * page_number) - page_size
            sql_find_card_transaction = sql_find_card_transaction + ' LIMIT {} OFFSET {} ;'.format(limit, offset)

            json_card_transaction = execute_statement(sql_find_card_transaction)
            
            if len(json_card_transaction["records"]) > 0:
                for this_transaction in json_card_transaction["records"]:
                    data_this_transaction = dict()
                    data_this_transaction["transaction_date"] = this_transaction[1]["stringValue"]
                    data_this_transaction["transaction_summary"] = this_transaction[4]["stringValue"]
                    data_this_transaction["transaction_spent"] = float(this_transaction[2]["stringValue"])
                    data_this_transaction["transaction_currency"] = this_transaction[3]["stringValue"]
                    data_this_transaction["card_type"] = card_type
                    data_this_transaction["card_id"] = card_id

                    value_dict = dict()
                    value_dict["card_type"] = card_type
                    value_dict["card_spent"] = data_this_transaction["transaction_spent"]
                    value_dict["transaction_currency"] = data_this_transaction["transaction_currency"]
                    earn_processing = calculate_earn_processing(value_dict)
                    data_this_transaction["card_score"] = earn_processing["card_score"]
                    data_this_transaction["card_campaign"] = earn_processing["card_campaign"]

                    score_unit = ""
                    if card_type == "scis_shopping":
                        score_unit = "points"
                    elif card_type == "scis_premiummiles" or card_type == "scis_platinummiles":
                        score_unit = "miles"
                    else:
                        score_unit = "cashback"
                    
                    data_this_transaction["score_unit"] = score_unit
                    data_individual_rewards_by_user_id_list.append(data_this_transaction)
            return json.dumps(data_individual_rewards_by_user_id_list)
        return "[]"
    except Exception:
        return traceback.format_exc()

@app.route('/transaction/add', methods=['POST'])
def add_transactions():
    """
    Add transactions to AWS Aurora's transaction table without using file
    Transactions with duplicated transaction ids will replace the exisitng transaction
    :param transactions: list of transactions (In JSON)
    Example input:
    {
        "transactions": [
            {
                "transaction_id": "c431cdc83abf302a55ba904426abdfa198ac18bbcfa1455cb9de5b2f351886d0", 
                "transaction_date": "2021-08-27",
                "amount": 279.95,
                "currency": "SGD",
                "merchant": "Cummerata Inc",
                "card_id": "0009dbf7-f94d-45f7-bd3a-973cd34a8516"
                "card_type": "scis_premiummiles"
            }
            , 
            {
                "transaction_id": "..."
            }
        ]
    }
    :type transactions: JSON Note: transaction_date must be in YYYY-MM-DD format, amount must be of type double
    :return: success status or error message
    :rtype: str

    """
    print("Preparing dataset")
    try: 
        parameter_sets = []
        # Key: card_id, value: Dictionary {'card_type': , 'card_spent': }
        card_total_spent = dict()
        for transaction in request.get_json(force=True)["transactions"]:
            parameters = [
                {'name': 'transaction_id', 'value': {'stringValue': transaction['transaction_id']}}, 
                {'name': 'transaction_date', 'typeHint': 'DATE', 'value': {'stringValue': transaction['transaction_date']}},
                {'name': 'transaction_amount', 'value': {'doubleValue': transaction['amount']}},
                {'name': 'transaction_currency', 'value': {'stringValue': transaction['currency']}},
                {'name': 'merchant', 'value': {'stringValue': transaction['merchant']}},
                {'name': 'card_id', 'value': {'stringValue': transaction['card_id']}},
                {'name': 'card_type', 'value': {'stringValue': transaction['card_type']}}
            ]
            parameter_sets.append(parameters)
            sql_query = "SELECT * from card WHERE card_id='" + transaction['card_id'] + "'"
            response = execute_statement(sql_query)
            # transaction['card_type'] = response["records"][0][2]["stringValue"]
            calculate_card_total_spent(card_total_spent, transaction)
        print("Updating cards scores in database")  
        update_card_score_databases(card_total_spent)
        print("Updating transaction data in database") 
        batch_execute_statement("REPLACE into transaction(transaction_id, transaction_date, transaction_amount, transaction_currency, merchant, card_id) VALUES(:transaction_id, :transaction_date, :transaction_amount, :transaction_currency, :merchant, :card_id)", parameter_sets, "TRANSACTION")
        return "Successfully added records"

    except Exception:
        return traceback.format_exc()

@app.route('/transaction/upload', methods=['POST'])
def upload_transactions():
    """
    Uploads transaction records to AWS Aurora's transaction table using spend.csv file
    Transactions with duplicated transaction ids will replace the exisitng transaction
    Also, it updates the score column in AWS Aurora's card table which means points for 
    SCIS Shopping card, miles for SCISPremiumMiles and PlatinumMiles card, cashback for 
    SCIS Freedom card
    TODO: Transactions with duplicated transaction ids as exisitng in Aurora database will NOT
    add score to any card, evem if its other values changed
    :param transaction_file: spend.csv file found in https://kaligo.exavault.com/files/spend
    :type transaction_file: File  
    :return: success status or error message
    :rtype: str

    """
    print("Preparing dataset")
    try: 
        df = pd.read_csv(request.files['transaction_file']) 
        transaction_parameter_sets = []
        # Key: card_id, value: Dictionary {'card_type': , 'card_spent': }
        card_total_spent = dict()
        for index, row in df.iterrows():
            transaction_parameters = [
                {'name': 'transaction_id', 'value': {'stringValue': row['transaction_id']}}, 
                {'name': 'transaction_date', 'typeHint': 'DATE', 'value': {'stringValue': row['transaction_date']}},
                {'name': 'transaction_amount', 'value': {'doubleValue': row['amount']}},
                {'name': 'transaction_currency', 'value': {'stringValue': row['currency']}}, 
                {'name': 'merchant', 'value': {'stringValue': row['merchant']}},
                {'name': 'card_id', 'value': {'stringValue': row['card_id']}}
            ]
            transaction_parameter_sets.append(transaction_parameters)
            calculate_card_total_spent(card_total_spent, row)
        print("Updating cards scores in database")  
        update_card_score_databases(card_total_spent)
        print("Updating transaction data in database")  
        batch_execute_statement("REPLACE into transaction(transaction_id, transaction_date, transaction_amount, transaction_currency, merchant, card_id) VALUES(:transaction_id, :transaction_date, :transaction_amount, :transaction_currency, :merchant, :card_id)", transaction_parameter_sets, "TRANSACTION")
        return ("Successfully updated " + str(len(df.index)) + " records")
    except Exception:
        return traceback.format_exc()

@app.route('/transaction/get', methods=['POST'])
def get_transactions(user_id = ""):
    """
    Return a dictionary of transactions as strings 

    :param page_size: Page size from range 1 to 8000 (8000 is roughly the max limit AWS aurora allows per transaction)
    :type page_size: Integer 
    :param page_number: Page number from range 1 to total number of records in transaction table/page_size
    :type page_number: Integer 
    :return: A dictionary, the records can be found under response["records"] or error message(str)
    :rtype: dictionary containing the key "records". Each record is of the following format [{"stringValue": transaction_id},
    {"stringValue": transaction_date}, {"stringValue": amount}, {"stringValue": currency}, {"stringValue": merchant}, 
    {"stringValue": card_id}]

    Sample output: 

    "records": [
        [
            {
                "stringValue": "1baebf324db9126a82681d739b82919c51f1574c00d4b0ab3d526e46f4e41393"
            },
            {
                "stringValue": "2021-08-27 00:00:00"
            },
            {
                "stringValue": "847.24"
            },
            {
                "stringValue": "SGD"
            },
            {
                "stringValue": "Baumbach  Okuneva and Predovic"
            },
            {
                "stringValue": "c50c8922-881d-490d-bd1f-aad6c124c778"
            }
        ],
        [
            {
                "stringValue": "9a5c92a364bee00915b30fc3b9b067dcdfcf256f487bb0cde985a7e9bb8afdda"
            },
            {
                "stringValue": "2021-08-27 00:00:00"
            },
            {
                "stringValue": "796.03"
            },
            {
                "stringValue": "SGD"
            },
            {
                "stringValue": "China Airlines"
            },
            {
                "stringValue": "0c80cea9-3f4e-44fb-95a7-3a84626a804a"
            }
        ]
    ]
    """
    page_size = int(request.form.get('page_size'))
    page_number = int(request.form.get('page_number'))
    try:     
        limit = page_size
        offset = (page_size * page_number) - page_size
        sql_query = "SELECT * from transaction ORDER BY transaction_date, merchant, transaction_amount"
        if user_id != "":
            sql_query_card = "SELECT * from card WHERE user_id='" + user_id + "'"
            response_card = execute_statement(sql_query_card)
            card_ids = []
            for i in range(len(response_card["records"])):
                card_ids.append("'" + response_card["records"][i][0]["stringValue"] + "'")
            card_ids_string = ", ".join(card_ids)
            # print("card_ids: " + card_ids_string)
            sql_query = "SELECT * from transaction WHERE card_id in (" + card_ids_string + ") ORDER BY transaction_date, merchant, transaction_amount"        
        sql_query = sql_query + ' LIMIT {} OFFSET {} ;'.format(limit, offset)
        json_response = execute_statement(sql_query)
        print("Retrieved " + str(len(json_response["records"])) + " records")
        return json_response
    except Exception:
        return traceback.format_exc()

@app.route('/transaction/get_by_user_id', methods=['POST'])
def get_transactions_by_user_id():
    return get_transactions(request.form.get('user_id'))

@app.route('/card/get_by_user_id', methods=['POST'])
def get_cards_by_user_id():
    """
    Return all the cards belonging to a user id, together with the score
    Score = points for SCIS Shopping card, miles for SCISPremiumMiles and PlatinumMiles card, cashback for SCIS Freedom card
    Run this function after uploading both users.csv and spend.csv file
    :param user_id: user_id found in users.csv file
    :type user_id: String 
    :return: A dictionary, the records can be found under response["records"] or error message(str)
    :rtype: dictionary containing the key "records". Each record is of the following format [{"stringValue": card_id},
    {"stringValue": user_id}, {"stringValue": card_type}, {"stringValue": score}]
    
    Sample output: 

    "records": [
        [
            {
                "stringValue": "23432c85-bcca-486e-89d5-86371397d83a"
            },
            {
                "stringValue": "b044eeea-5818-461b-a005-372b0ee53647"
            },
            {
                "stringValue": "scis_freedom"
            },
            {
                "stringValue": "0.000"
            }
        ],
        [
            {
                "stringValue": "17cc3eca-c920-4e83-83fd-e1bb9f89ca75"
            },
            {
                "stringValue": "b044eeea-5818-461b-a005-372b0ee53647"
            },
            {
                "stringValue": "scis_shopping"
            },
            {
                "stringValue": "0.000"
            }
        ]
    ]
    """
    user_id = request.form.get('user_id')
    try:
        sql_query = "SELECT * from card WHERE user_id='" + user_id + "' ORDER BY card_type"
        json_response = execute_statement(sql_query)
        # print(json_response)
        print("Retrieved " + str(len(json_response["records"])) + " records")
        return json_response
    except Exception:
        return traceback.format_exc()

@app.route('/user/get_reward_by_user_id', methods=['POST'])
def get_rewards_by_user_id():
    """
    Return the rewards (points/miles/cashback) by user id
    Run this function after uploading both users.csv and spend.csv file
    :param user_id: user_id found in users.csv file
    :type user_id: String  
    :return: A dictionary containing points, miles and cashback keys
    :rtype: dictionary 
    Sample output: 
    {
        "points": 74.365,
        "miles": 0,
        "cashback": 59.2
    }
    """
    rewards = {"points": 0, "miles": 0, "cashback": 0}
    for record in get_cards_by_user_id()["records"]:
        if record[2]["stringValue"] == "scis_shopping":
            rewards["points"] += float(record[3]["stringValue"])
        elif record[2]["stringValue"] == "scis_premiummiles" or record[2]["stringValue"] == "scis_platinummiles":
            rewards["miles"] +=  float(record[3]["stringValue"])
        elif record[2]["stringValue"] == "scis_freedom":
            rewards["cashback"] +=  float(record[3]["stringValue"])
    return rewards

@app.route('/campaign/view_campaigns', methods=['GET'])
def view_campaigns():
    
    """
    Return the list of existing camapaigns and its respective details 
    Run this function when the campaign management portal is logged into
    :return: An array of jsons containing card program name, a description of the campaign, spend type, rewards type, and reward currency
    :rtype: array
    Sample output:
    [
        {
            cardProgram: 'SCIS Shopping Card',
            desc: '4 miles per dollar with Grab, min spend 100 SGD',
            spend: 1,
            reward: 4,
            rewardCurrency: 'miles',
            MCC: 5999           
        },
        {
            cardProgram: 'SCIS Shopping Card',
            desc: '4 miles per dollar with Grab, min spend 100 SGD',
            spend: 1,
            reward: 4,
            rewardCurrency: 'miles',
            MCC: 5999           
        }
    ]
    """
    try:
        sql_query = "SELECT * from campaign;"
        json_response = execute_statement(sql_query)
        # print(json_response)
        print("Retrieved " + str(len(json_response["records"])) + " records")
        return { "campaigns": json_response["records"]}
    except Exception:
        return traceback.format_exc()

@app.route('/campaigns/add_default_campaigns', methods=['GET'])
def add_default_campaigns():
    """
    Add campaigns into AWS Aurora
    """
    used_campaign_ids = set()
    existing_campaigns = [
        {
            'campaign_id': 1,
            'card_type': 'SCIS Shopping Card',
            'campaign_desc': '4 miles per dollar with Grab, min spend 100 SGD',
            'perSpend': 1,
            'reward': 4,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 100,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        },
        {
            'campaign_id': 2,
            'card_type': 'SCIS PremiumMiles',
            'campaign_desc': '6 miles per dollar on all spend with Kaligo.com',
            'perSpend': 1,
            'reward': 6,
            'rewardCurrency': 'miles',
            'mcc': '',
            'minSpend': 0,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        },
        {
            'campaign_id': 3,
            'card_type': 'SCIS PlatinumMiles',
            'campaign_desc': '10 miles per dollar on all spend with Kaligo.com',
            'perSpend': 1,
            'reward': 10,
            'rewardCurrency': 'miles',
            'mcc': '4555,4556',
            'minSpend': 0,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        },
        {
            'campaign_id': 4,
            'card_type': 'SCIS Freedom',
            'campaign_desc': '5% cashback on all petrol spend with Shell till 31 December 2021',
            'perSpend': 1,
            'reward': 0.05,
            'rewardCurrency': 'cashback',
            'mcc': '',
            'minSpend': 0,
            'validUntil': '2021-12-31 23:59:59',
            'isActive': 1
        }
    ]
    campaign_parameters_sets = []
    for campaign in existing_campaigns:
        campaign_parameters = [
            {'name': 'campaign_id', 'value': {'stringValue': str(campaign['campaign_id'])}}, 
            {'name': 'card_type', 'value': {'stringValue': str(campaign['card_type'])}},
            {'name': 'campaign_desc', 'value': {'stringValue': str(campaign['campaign_desc'])}},
            {'name': 'perSpend', 'value': {'stringValue': str(campaign['perSpend'])}},
            {'name': 'reward', 'value': {'stringValue': str(campaign['reward'])}},
            {'name': 'rewardCurrency', 'value': {'stringValue': str(campaign['rewardCurrency'])}},
            {'name': 'mcc', 'value': {'stringValue': str(campaign['mcc'])}},
            {'name': 'minSpend', 'value': {'stringValue': str(campaign['minSpend'])}},
            {'name': 'validUntil', 'value': {'stringValue': str(campaign['validUntil'])}},
            {'name': 'isActive', 'value': {'stringValue': str(campaign['isActive'])}},
        ]
        campaign_parameters_sets.append(campaign_parameters)
    
    try:
        print("Adding default campaigns data in database")    
        batch_execute_statement("INSERT into campaign\
        (campaign_id, card_type, campaign_desc, perSpend, reward, rewardCurrency, mcc, minSpend, validUntil, isActive)\
        VALUES(:campaign_id, :card_type, :campaign_desc, :perSpend, :reward, :rewardCurrency, :mcc, :minSpend, :validUntil, :isActive)\
        ON DUPLICATE KEY UPDATE\
        campaign_id=:campaign_id, card_type=:card_type, campaign_desc=:campaign_desc, perSpend=:perSpend, reward=:reward, rewardCurrency=:rewardCurrency, mcc=:mcc, minSpend=:minSpend, validUntil=:validUntil, isActive=:isActive\
        ", campaign_parameters_sets, "CAMPAIGN")
        return "Successfully Added Default Campaigns"
    except Exception:
        return traceback.format_exc()
    
@app.route('/campaigns/add_campaigns', methods=['POST'])
def add_campaigns():
    try:
        new_campaigns = request.get_json(force=True)["campaigns"]
        campaign_parameters_sets = []
        for campaign in new_campaigns:
            campaign_parameters = [
                {'name': 'campaign_id', 'value': {'stringValue': str(campaign['campaign_id'])}}, 
                {'name': 'card_type', 'value': {'stringValue': str(campaign['card_type'])}},
                {'name': 'campaign_desc', 'value': {'stringValue': str(campaign['campaign_desc'])}},
                {'name': 'perSpend', 'value': {'stringValue': str(campaign['perSpend'])}},
                {'name': 'reward', 'value': {'stringValue': str(campaign['reward'])}},
                {'name': 'rewardCurrency', 'value': {'stringValue': str(campaign['rewardCurrency'])}},
                {'name': 'isActive', 'value': {'stringValue': str(campaign['isActive'])}},
            ]
            if 'mcc' in campaign:
                campaign_parameters.append({'name': 'mcc', 'value': {'stringValue': str(campaign['mcc'])}})
            else:
                campaign_parameters.append({'name': 'mcc', 'value': {'stringValue': ''}})
            if 'minSpend' in campaign:
                campaign_parameters.append({'name': 'minSpend', 'value': {'stringValue': str(campaign['minSpend'])}})
            else:
                campaign_parameters.append({'name': 'minSpend', 'value': {'stringValue': str(0)}})
            if 'validUntil' in campaign:
                campaign_parameters.append({'name': 'validUntil', 'value': {'stringValue': str(campaign['validUntil'])}})
            else:
                campaign_parameters.append({'name': 'validUntil', 'value': {'stringValue': '1900-01-01 00:00:00'}})
                    
            campaign_parameters_sets.append(campaign_parameters)
        print("Adding default campaigns data in database")    
        batch_execute_statement("INSERT into campaign\
        (campaign_id, card_type, campaign_desc, perSpend, reward, rewardCurrency, mcc, minSpend, validUntil, isActive)\
        VALUES(:campaign_id, :card_type, :campaign_desc, :perSpend, :reward, :rewardCurrency, :mcc, :minSpend, :validUntil, :isActive)\
        ON DUPLICATE KEY UPDATE\
        campaign_id=:campaign_id, card_type=:card_type, campaign_desc=:campaign_desc, perSpend=:perSpend, reward=:reward, rewardCurrency=:rewardCurrency, mcc=:mcc, minSpend=:minSpend, validUntil=:validUntil, isActive=:isActive\
        ", campaign_parameters_sets, "CAMPAIGN")
        return "Successfully Added New Campaigns"
    except Exception:
        return traceback.format_exc()

@app.route('/campaign/update_campaign_status', methods=['POST'])
def update_campaign_status():
    try:
        data = request.get_json(force=True)
        
        return "Successfully deleted campaign"
    except Exception:
        return traceback.format_exc()

@app.route('/campaign/subscribe', methods=['POST'])
def subscribe():
    """
    Accepts a JSON containing an email address
    The user must confirm the email subscription in their email inbox 
    to start receiving campaign subscription
    """
    req =request.get_json(force=True)
    params = { "endpoint": req["email"], "topicArn": config("TOPIC_ARN"), "protocol": "Email"}
    response = requests.post(url= config("SNS_URL") + "/subscribe",params=params).text
    return response

@app.route('/campaign/send_email', methods=['POST'])
def send_email():
    """
    Accepts a JSON containing the message and send to all subscribed emails 
    Users must first subscribe using "/campaign/subscribe" and then confirm the email subscription in their email inbox
    """
    req =request.get_json(force=True)
    params = { "message": req["message"], "topicArn": config("TOPIC_ARN") }
    response = requests.post(url= config("SNS_URL") + "/send_email",params=params).text
    return response
if __name__ == "__main__":
    app.run(debug=True, threaded=True)