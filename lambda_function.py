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
        # if match start cognito flow
        # else 401 Unauthorized
    else:
        return client_error("Unknow auth operation: '{}'".format(operation))

    return "Logged In"

def users(event, context, operation):
    # user_operations = {
    #     'put': lambda x: dynamo.put_item(**x),
    #     'get': lambda x: dynamo.get_item(**x),
    #     'delete': lambda x: dynamo.delete_item(**x),
    #     'get_collection': lambda x: dynamo.scan(**x)
    # }
    pass


def cafes(event, context, operation):
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
    return "ERROR::CLIENT::{}::{}".format(http_status_code, message)

def match_password(client_supplied_password, hashed_password_on_record):
    # @TODO issue/#1
    # import bcrypt
    # return bcrypt.hashpw(client_supplied_password, hashed_password_on_record) == hashed_password_on_record
    # ========
    # just clear text for proof of concept phase :|
    return client_supplied_password == hashed_password_on_record
