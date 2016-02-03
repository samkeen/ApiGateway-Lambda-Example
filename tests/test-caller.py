import boto3

# create a client, but configure with Cognito returned credentials

# make call to getItem for DynamoDb cafes table

# see: http://boto3.readthedocs.org/en/latest/reference/core/session.html

table_name = 'cafes'

# mapping
#
#    cognito.get_credentials_for_identity response:
#
#    Credentials': {
#      SecretKey' >> aws_secret_access_key
#      SessionToken >> aws_session_token
#      Expiration': datetime.datetime(2016, 2, 1, 17, 5, 50, tzinfo=tzlocal()),
#      AccessKeyId >> aws_access_key_id
#    }
#

session = boto3.session.Session(
    region_name='us-west-2',
    aws_access_key_id='<Cognito.Credentials.AccessKeyId>',
    aws_secret_access_key='<Cognito.Credentials.SecretKey>',
    aws_session_token='<Cognito.Credentials.SessionToken>'
)
dynamo = session.resource('dynamodb').Table(table_name)

results = dynamo.scan()

print(results)
