from database_handler import *
rds_transaction = begin_transaction()
execute_statement("DROP TABLE IF EXISTS card", rds_transaction)
execute_statement("CREATE TABLE IF NOT EXISTS card (\
  card_id varchar(36) NOT NULL,\
  user_id varchar(36) NOT NULL,\
  card_type varchar(45) NOT NULL,\
  score decimal(15,3) DEFAULT 0,\
  PRIMARY KEY (card_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE card", rds_transaction)

execute_statement("CREATE TABLE IF NOT EXISTS mcc (\
  mcc_id int(11) NOT NULL,\
  mcc_category varchar(255) NOT NULL,\
  PRIMARY KEY (mcc_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE mcc", rds_transaction)

execute_statement("CREATE TABLE IF NOT EXISTS merchant (\
  merchant_id int(11) NOT NULL,\
  merchant_name varchar(45) NOT NULL,\
  MCC_mcc_id int(11) NOT NULL,\
  PRIMARY KEY (merchant_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE merchant", rds_transaction)

execute_statement("CREATE TABLE IF NOT EXISTS program (\
  program_id int(11) NOT NULL,\
  card_id int(11) NOT NULL,\
  program_name varchar(45) NOT NULL,\
  PRIMARY KEY (program_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE program", rds_transaction)

execute_statement("CREATE TABLE IF NOT EXISTS reward (\
  reward_id int(11) NOT NULL,\
  reward_type varchar(45) DEFAULT NULL,\
  reward_remark varchar(45) DEFAULT NULL,\
  PRIMARY KEY (reward_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE reward", rds_transaction)
execute_statement("DROP TABLE IF EXISTS transaction", rds_transaction)
execute_statement("CREATE TABLE IF NOT EXISTS transaction (\
  transaction_id varchar(64) NOT NULL,\
  transaction_date datetime NOT NULL,\
  transaction_amount decimal(9,2) NOT NULL,\
  transaction_currency varchar(5) NOT NULL,\
  merchant varchar(256) NOT NULL,\
  card_id varchar(36) NOT NULL,\
  PRIMARY KEY (transaction_id)\
)", rds_transaction)

execute_statement("TRUNCATE TABLE transaction", rds_transaction)

execute_statement("DROP TABLE IF EXISTS user", rds_transaction)
execute_statement("CREATE TABLE IF NOT EXISTS user (\
  user_id varchar(36) NOT NULL,\
  user_name varchar(256) NOT NULL,\
  user_password varchar(256) NOT NULL,\
  PRIMARY KEY (user_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE user", rds_transaction)

execute_statement("DROP TABLE IF EXISTS campaign", rds_transaction)
execute_statement("CREATE TABLE IF NOT EXISTS campaign (\
  campaign_id int(11) NOT NULL,\
  card_type varchar(45) NOT NULL,\
  campaign_desc varchar(100) NOT NULL,\
  perSpend decimal(15,3) DEFAULT 0,\
  reward decimal(15,3) DEFAULT 0,\
  rewardCurrency varchar(45),\
  mcc varchar(45),\
  minSpend decimal(15,3) DEFAULT 0,\
  validUntil datetime,\
  isActive TINYINT(1) DEFAULT 1,\
  PRIMARY KEY (campaign_id)\
)", rds_transaction)
execute_statement("TRUNCATE TABLE campaign", rds_transaction)

print(commit_transaction(rds_transaction))
