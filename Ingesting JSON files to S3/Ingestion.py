# Importing dependencies
import boto3
from AWSkeys import AccessKey, SecretAccessKey
import os, os.path

# Defining parameters
path = '/home/andreolv/Downloads/Empresa/Files/'
bucketname = 'andreyempresa'
location = 'us-east-2'

# Conecting session to AWS
s3 = boto3.client(
    's3',
    aws_access_key_id=AccessKey,
    aws_secret_access_key=SecretAccessKey,
    region_name = location
)

# Create bucket
s3.create_bucket(Bucket=bucketname, CreateBucketConfiguration={'LocationConstraint': location})

# Read the name of all files in the directory and put them in a list
lista_arquivos = os.listdir(path)

# Upload files to S3
for i in lista_arquivos:
    s3.upload_file(path + i, bucketname, i)
    print("Upload Successful "+i)
   
"""
Sugestions for improvements:
- Generalize code for read pathfiles for other directories structure
- Add try/except to catch exceptions and print the error messages
- Validade the structure of json files before upload to garante the integrity of the input data
"""