
# Architecture at a glance (Multi Region Deployment replicated in Seoul & Singapore Regions)
![image](https://user-images.githubusercontent.com/65384703/186190905-7dcc945e-559f-41e4-9e3e-de3c1dfc4c84.png)



# Installation instructions for backend
Steps to execute application:
1. cd flask-server
2. install requirement package 
    pip install -r requirements.txt
3. run application:
    python application.py

# Performance For Uploading Spend and User files
## Case #1:
- File uploaded: spend.csv (2,266,985 rows)
- Time to upload and write to RDS: 12min 14s 
- EBS Logs file: 1-web.stdout.log
<br>

## Case #2:
- File uploaded: spend.csv (1,000,000 rows)
- Time to upload and write to RDS: 7min 12s
- EBS Logs file: 2-web.stdout.log
<br>

# Obtain Log Files
To obtain log files please do the following:
- Go to: AWS Console > Elastic Beanstalk > Itsag1t42022backend2-env > Logs > Request Full Logs > Download All Zip Files (or just download the zip file for instance id i-0b3e53456dd355cba)
- Unzip the files and go to path /var/log/web.stdout.log

# Notes & Acknowledgement
Reuploaded from a private organization as part of SMU-X Project IT-Solution Architecture CS301
AWS Infrastructure has been torn down. This repo won't run as keys are managed by AWS Secrets Manager which has been long deactivated. 
Contributors: @ssjuan, @simshengqin, @nicoonnicolas, @givemewaffles, @rxtan
