from sharepoint import SharePoint
import re
import sys, os, json
import boto3
from botocore.exceptions import ClientError

# 1 args = SharePoint folder name. May include subfolders YouTube/2022
folder_name = sys.argv[1]
# 2 args = locate or remote folder_dest
folder_dest = sys.argv[2]
# 3 args = SharePoint file name. This is used when only one file is being downloaded
file_name = sys.argv[3]
# 4 args = SharePoint file name pattern
file_name_pattern = sys.argv[4]


# read json file
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = '\\'.join([ROOT_DIR, 'config.json'])

with open(config_path) as config_file:
    config = json.load(config_file)
    config = config['aws_bucket']

AWS_ACCESS_KEY_ID = config['aws_access_key_id']
AWS_SECRET_ACCESS_KEY = config['aws_secret_access_key']
BUCKET = config['bucket_name']
BUCKET_SUBFOLDER = config['bucket_subfolder']

# functions used for aws
def upload_file_to_s3(file_dir_path, bucket, file_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    try:
        response = s3_client.upload_file(file_dir_path, bucket, file_name)
    except ClientError as e:
        print(e)
        return False
    return True
        

def bucket_subfolder_build(BUCKET_SUBFOLDER, file_name):
    if BUCKET_SUBFOLDER != '':
        file_path_name = '/'.join([BUCKET_SUBFOLDER, file_name])
        return file_path_name
    else:
        return file_name

def save_file(file_n, file_obj):
    file_dir_path = '\\'.join([folder_dest, file_n])
    with open(file_dir_path, 'wb') as f:
        f.write(file_obj)
        f.close()

def get_file(file_n, folder):
    file_obj = SharePoint().download_file(file_n, folder)
    save_file(file_n, file_obj)
    file_dir_path = '\\'.join([folder_dest, file_n])
    file_name = bucket_subfolder_build(BUCKET_SUBFOLDER, file_n)
    upload_file_to_s3(file_dir_path, BUCKET, file_name)

def get_files(folder):
    files_list = SharePoint().download_files(folder)
    for file in files_list:
        get_file(file['Name'], folder)

def get_files_by_pattern(pattern, folder):
    files_list = SharePoint().download_files(folder)
    for file in files_list:
        if re.search(pattern, file['Name']):
            get_file(file['Name'], folder)

if __name__ == '__main__':
    if file_name != 'None':
        get_file(file_name, folder_name)
    elif file_name_pattern != 'None':
        get_files_by_pattern(file_name_pattern, folder_name)
    else:
        get_files(folder_name)