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
        raise ValueError("'resource' parameter required")
    if not operation:
        raise ValueError("'operation' parameter required")
    resource = resource.lower()
    operation = operation.lower()

    resource_routes = {
        'debug': lambda event, context, operation: debug(event, context, operation),
        'users': lambda event, context, operation: users(event, context, operation),
        'cafe': lambda event, context, operation: cafes(event, context, operation),
    }

    if resource not in resource_routes:
        raise ValueError("Unknown resource: '{}'".format(resource))

    return resource_routes[resource](event, context, operation)


def debug(event, context, operation):
    debug_operations = {
        'echo': lambda x: x,
        'ping': lambda x: 'pong'
    }
    if operation not in debug_operations:
        raise ValueError('Unrecognized operation: {}'.format(operation))

    return debug_operations[operation](event.get('payload'))


def users(event, context, operation):
    pass


def cafes(event, context, operation):
    dynamo_operations = {
        'put': lambda x: dynamo.put_item(**x),
        'get': lambda x: dynamo.get_item(**x),
        'delete': lambda x: dynamo.delete_item(**x),
        'get_collection': lambda x: dynamo.scan(**x)
    }

    if operation not in dynamo_operations:
        raise ValueError('Unrecognized operation: {}'.format(operation))

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
    return dynamo_operations[operation](payload)
