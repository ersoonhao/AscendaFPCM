import boto3
from decouple import config

cluster_arn = config("SEOUL_CLUSTER_ARN_SERVERLESS")
secret_arn = config("SEOUL_SECRET_ARN")
rdsData = boto3.client('rds-data',  region_name='ap-northeast-2')

def begin_transaction():
    return rdsData.begin_transaction(
    resourceArn = cluster_arn,
    secretArn = secret_arn,
    database = 'g1t42')
def execute_statement(sql, rds_transaction = -1, parameters = []):
    try:
        if rds_transaction == -1 or len(parameters) == 0:
            # SELECT statement => Do not need parameters or transaction id as it is executed immediately
            response = rdsData.execute_statement(resourceArn=cluster_arn,
                                        secretArn=secret_arn,
                                        database='g1t42',
                                        sql=sql)
        else:
            #INSERT statement => Need parameters and transaction id obtained from begin_transaction()
            #Then, run any number of execute statement() and then run commit_transaction() at the end
            response = rdsData.execute_statement(resourceArn=cluster_arn,
                                        secretArn=secret_arn,
                                        database='g1t42',
                                        sql=sql,
                                        transactionId = rds_transaction['transactionId'], 
                                        parameters = parameters)
            # print(response["numberOfRecordsUpdated"])
        return response
    except Exception:
        # Pass back the exception to the caller to handle
        raise
def commit_transaction(rds_transaction):
    rds_transaction = rdsData.commit_transaction(
    resourceArn = cluster_arn,
    secretArn = secret_arn,
    transactionId = rds_transaction['transactionId'])
    # print(rds_transaction['transactionStatus'], end=" ")

def rollback_transaction(rds_transaction):
    rds_transaction = rdsData.commit_transaction(
    resourceArn = cluster_arn,
    secretArn = secret_arn,
    transactionId = rds_transaction['transactionId'])

def batch_execute_statement(sql, parameter_sets, msg=""):
    # Used for executing multiple insert statements as a much faster alternative to running a lot of execute statements
    print("Started uploading")    
    chunk_count = 1
    rds_transaction = -1
    try:     
        # batch_execute_statement seems to only be able to support 8k rows at one go
        # Hence, split the statements into chunks of 5000 - 8k rows and run the transactions seperately (Reduce if receive connection error)
        # Reduce the chunk_size the more columns you are trying to insert per row
        chunk_size = 8000
        for i in range(0, len(parameter_sets), chunk_size):
            parameter_set_chunk = parameter_sets[i:i+chunk_size]
            rds_transaction = begin_transaction()
            rdsData.batch_execute_statement(resourceArn=cluster_arn,
                                        secretArn=secret_arn,
                                        database='g1t42',
                                        sql=sql,
                                        transactionId = rds_transaction['transactionId'],
                                        parameterSets = parameter_set_chunk)
            commit_transaction(rds_transaction)
            print(msg + " : " + str(i) + " to " + str(min(i+chunk_size, len(parameter_sets))) + " out of " + str(len(parameter_sets)) + " records")
            chunk_count += 1
        print("Finished uploading")
    except Exception as e:
        if rds_transaction != -1:
            rollback_transaction(rds_transaction)
        # Pass back the exception to the caller to handle
        raise