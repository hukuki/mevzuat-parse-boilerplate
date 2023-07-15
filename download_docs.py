from botocore.config import Config
import boto3
import json

#open the json file
with open('mevzuat-ids-eren.json') as json_file:
    mevzuat_ids = json.load(json_file)

#download the files from s3
access_key_id = 'AKIA2VFJCEIUNUOLXQFF'
secret_access_key = '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'



s3 = boto3.client('s3', 
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
)



#for mevzuat_id in mevzuat_ids:
    #s3.download_file('hukuki-yedek', f'mevzuat/{mevzuat_id}', f'mevzuat-raw/{mevzuat_id}.doc')

s3.download_file('hukuki-yedek', f'mevzuat/64486b58e0b1ea631dea7927', f'64486b58e0b1ea631dea7927.doc')




