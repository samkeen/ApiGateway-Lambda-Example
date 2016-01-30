from __future__ import print_function

import boto3


def lambda_handler(event, context):
    """
    Simple front controller for the few resource methods of this example

    :param event:
    :param context:
    :return:
    """
    resource = event.get('resource')
    operation = event.get('operation')
    if not resource:
        return client_error("'resource' parameter required")
    if not operation:
        return client_error("'operation' parameter required")
    resource = resource.lower()
    operation = operation.lower()

    resource_routes = {
        'auth': lambda event, context, operation: auth(event, context, operation),
        'users': lambda event, context, operation: users(event, context, operation),
        'cafe': lambda event, context, operation: cafes(event, context, operation),
    }

    if resource not in resource_routes:
        return client_error("Unknown resource: '{}'".format(resource))

    return resource_routes[resource](event, context, operation)


def auth(event, context, operation):
    """
    All the Authentication/Authorization concerns for the app
    :param event:
    :param context:
    :param operation:
    :return:
    """
    if operation == 'login':
        table_name = 'cafe_users'
        dynamo = boto3.resource('dynamodb').Table(table_name)
        username = event.get('username')
        client_supplied_password = event.get('password')
        if not username or not client_supplied_password:
            return client_error("Missing required parameters 'username' and/or 'password")
        user_response = dynamo.get_item(
                Key={
                    'username': username
                }
        )
        if 'Item' not in user_response:
            return client_error("username and/or password incorrect", 401)
        user_item = user_response['Item']
        if not match_password(client_supplied_password, user_item['password']):
            return client_error("username and/or password incorrect", 401)
        print("User Found: {}".format(user_item))
        # start cognito flow using the "Developer Authenticated Identities" work flow
        # see: mobile.awsblog.com/post/Tx1YVAQ4NZKBWF5/Amazon-Cognito-Announcing-Developer-Authenticated-Identities
        # see: mobile.awsblog.com/post/Tx2FL1QAPDE0UAH/Understanding-Amazon-Cognito-Authentication-Part-2-Developer-Authenticated-Ident
        cognito = boto3.client('cognito-identity', region_name='us-east-1')
        response = cognito.get_open_id_token_for_developer_identity(
                IdentityPoolId='<AWS REGION>:<UUID>',
                Logins={
                    'serverless-demo.qstratus.com': user_item['username']
                }
        )
        # {Token: '', IdentityId: '', ResponseMetadata: {}}
        print("Cognito Response IdentityId: {}".format(response['IdentityId']))
        identity = cognito.get_credentials_for_identity(
            IdentityId=response['IdentityId'],
            Logins={
                'cognito-identity.amazonaws.com': response['Token']
            }
        )
        print("Identity: {}".format(identity))



    else:
        return client_error("Unknow auth operation: '{}'".format(operation))

    return "Logged In"


def users(event, context, operation):
    """
    All the User account concerns for the App
    :param event:
    :param context:
    :param operation:
    :return:
    """
    pass


def cafes(event, context, operation):
    """
    This is the example Resource for the App.  This is a App User contributed resource
    :param event:
    :param context:
    :param operation:
    :return:
    """
    cafe_operations = {
        'put': lambda x: dynamo.put_item(**x),
        'get': lambda x: dynamo.get_item(**x),
        'delete': lambda x: dynamo.delete_item(**x),
        'get_collection': lambda x: dynamo.scan(**x)
    }

    if operation not in cafe_operations:
        return client_error('Unrecognized cafe operation: {}'.format(operation))

    table_name = 'cafes'
    dynamo = boto3.resource('dynamodb').Table(table_name)

    payload = {}
    if operation in ('get', 'delete'):
        payload = {
            "Key": event.get('payload')
        }
    elif operation == 'put':
        payload = {
            "Item": event.get('payload')
        }
    return cafe_operations[operation](payload)


def client_error(message, http_status_code=400):
    """
    Simple util function to return an error in a consistent format to the calling
    system (API Gateway in this case.

    :param message:
    :param http_status_code:
    :return:
    """
    return "ERROR::CLIENT::{}::{}".format(http_status_code, message)


def match_password(client_supplied_password, hashed_password_on_record):
    # @TODO issue/#1
    # import bcrypt
    # return bcrypt.hashpw(client_supplied_password, hashed_password_on_record) == hashed_password_on_record
    # ========
    # just clear text for proof of concept phase :|
    return client_supplied_password == hashed_password_on_record
