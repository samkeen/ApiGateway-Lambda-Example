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
    request_payload = event.get('payload')
    print("recieved event: '{}'".format(event))
    if not resource:
        return client_error("'resource' parameter required")
    if not operation:
        return client_error("'operation' parameter required")
    if 'payload' not in event:
        return client_error("'payload' parameter required")
    resource = resource.lower()
    operation = operation.lower()

    resource_routes = {
        'auth': lambda payload, context, operation: auth(request_payload, context, operation),
        'users': lambda payload, context, operation: users(request_payload, context, operation),
        'cafe': lambda payload, context, operation: cafes(request_payload, context, operation),
    }

    if resource not in resource_routes:
        return client_error("Unknown resource: '{}'".format(resource))

    return resource_routes[resource](event, context, operation)


def auth(payload, context, operation):
    """
    All the Authentication/Authorization concerns for the app
    :param payload:
    :param operation:
    :return:
    """
    print("Operation: '{}', payload: {}".format(operation, payload))
    if operation == 'login':
        table_name = 'cafe_users'
        dynamo = boto3.resource('dynamodb').Table(table_name)
        if 'username' not in payload or 'password' not in payload:
            return client_error("Missing required parameters 'username' and/or 'password'")
        username = payload['username']
        client_supplied_password = payload['password']
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
        print("User Found: {}".format(user_item))
        # start cognito flow using the "Developer Authenticated Identities" work flow
        # see: mobile.awsblog.com/post/Tx1YVAQ4NZKBWF5/Amazon-Cognito-Announcing-Developer-Authenticated-Identities
        # see: mobile.awsblog.com/post/Tx2FL1QAPDE0UAH/Understanding-Amazon-Cognito-Authentication-Part-2-Developer-Authenticated-Ident
        cognito = boto3.client('cognito-identity', region_name='us-east-1')
        response = cognito.get_open_id_token_for_developer_identity(
                IdentityPoolId='us-east-1:489dd764-1fd3-4e2a-9c7b-0be784d24aba',
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


def users(payload, context, operation):
    """
    All the User account concerns for the App
    :param payload:
    :param context:
    :param operation:
    :return:
    """
    pass


def cafes(payload, context, operation):
    """
    This is the example Resource for the App.  This is a App User contributed resource
    :param payload:
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

    call_payload = {}
    if operation in ('get', 'delete'):
        call_payload = {
            "Key": payload
        }
    elif operation == 'put':
        call_payload = {
            "Item": payload
        }
    print("Calling Dynamo, operation: '{}', with call_payload: {}".format(operation, call_payload))
    return cafe_operations[operation](call_payload)


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
