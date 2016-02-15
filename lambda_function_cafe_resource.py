from __future__ import print_function

import boto3


def lambda_handler(event, context):
    """
    Simple front controller for the few resource methods of this example

    :param event:
    :param context:
    :return:
    """
    operation = event.get('operation')
    request_payload = event.get('payload')
    print("received event: '{}'".format(event))
    if not operation:
        return client_error("'operation' parameter required")
    if 'payload' not in event:
        return client_error("'payload' parameter required")
    operation = operation.lower()

    return cafes(request_payload, operation)


def cafes(payload, operation):
    """
    This is the example Resource for the App.  This is a App User contributed resource
    :param payload:
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
