from __future__ import print_function

import boto3


class ClientError(Exception):
    pass


def lambda_handler(event, context):
    """
    Simple front controller for the few resource methods of this example

    :param event:
    :param context:
    :return:
    """

    ### START :: NEED FILL IN THESE VALUES ###################################
    COGNITO_REGION = ''
    # IDENTITY_PROVIDER_NAME is found under 'Authentication providers' -> 'Custom' Tab
    DEVELOPER_PROVIDER_NAME = ''
    IDENTITY_POOL_ID = ''
    ### END :: NEED FILL IN THESE VALUES #####################################

    USERS_TABLE_NAME = 'ServerlessCafe_users'

    request_payload = event.get('payload')
    print("received event: '{}'".format(event))
    if 'payload' not in event:
        return client_error("'payload' parameter required")

    dynamo = boto3.resource('dynamodb').Table(USERS_TABLE_NAME)
    if 'username' not in request_payload or 'password' not in request_payload:
        return client_error("Missing required parameters 'username' and/or 'password'")
    username = request_payload['username']
    client_supplied_password = request_payload['password']
    user_response = dynamo.get_item(
        Key={
            'username': username
        }
    )
    if 'Item' not in user_response:
        return client_error("username and/or password incorrect", 401)
    user_item = user_response['Item']
    print("User found: {}".format(user_item))
    if not match_password(client_supplied_password, user_item['password']):
        return client_error("username and/or password incorrect", 401)
    # start cognito flow using the "Developer Authenticated Identities" work flow
    # see: mobile.awsblog.com/post/Tx1YVAQ4NZKBWF5/Amazon-Cognito-Announcing-Developer-Authenticated-Identities
    # see: mobile.awsblog.com/post/Tx2FL1QAPDE0UAH/Understanding-Amazon-Cognito-Authentication-Part-2-Developer-Authenticated-Ident
    cognito = boto3.client('cognito-identity', region_name=COGNITO_REGION)
    logins = {}
    logins[DEVELOPER_PROVIDER_NAME] = user_item['username']
    response = cognito.get_open_id_token_for_developer_identity(
        IdentityPoolId=IDENTITY_POOL_ID,
        Logins=logins,
        TokenDuration=900  # default 900 sec (15 min), max 24hrs
    )
    print("OpenIdToken: {}".format(response['Token']))
    # {Token: '', IdentityId: '', ResponseMetadata: {}}
    print("Cognito Response IdentityId: {}".format(response['IdentityId']))
    identity = cognito.get_credentials_for_identity(
        IdentityId=response['IdentityId'],
        Logins={
            'cognito-identity.amazonaws.com': response['Token']
        }
    )
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(identity)
    return format_credentials_response(identity['Credentials'])


def format_credentials_response(credentials):
    """

    :param credentials:
    :return:
    """
    return {
        'status_code': 200,
        'message': 'Temporary credentials',
        'payload': {
            'access_key_id': credentials['AccessKeyId'],
            'expiration': credentials['Expiration'].strftime('%s'),
            'secret_key': credentials['SecretKey'],
            'session_token': credentials['SessionToken']
        }
    }


def client_error(message, http_status_code=400):
    """
    Simple util function to return an error in a consistent format to the calling
    system (API Gateway in this case.

    :param message:
    :param http_status_code:
    :return:
    """

    client_error = ClientError("status_code:={}|message:={}".format(http_status_code, message))
    raise client_error


def match_password(client_supplied_password, hashed_password_on_record):
    # @TODO issue/#1
    # import bcrypt
    # return bcrypt.hashpw(client_supplied_password, hashed_password_on_record) == hashed_password_on_record
    # ========
    # just clear text for proof of concept phase :|
    return client_supplied_password == hashed_password_on_record
