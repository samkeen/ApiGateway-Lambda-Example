from __future__ import print_function

import boto3
import json

print('Loading function')


def lambda_handler(event, context):
    """Provide an event that contains the following keys:

      - method: one of the operations in the operations dict below
      - payload: a parameter to pass to the operation being performed
    """
    # print("Received event: " + json.dumps(event, indent=2))

    debug_operations = {
        'echo': lambda x: x,
        'ping': lambda x: 'pong'
    }
    dynamo_operations = {
        'PUT': lambda x: dynamo.put_item(**x),
        'GET': lambda x: dynamo.get_item(**x),
        'DELETE': lambda x: dynamo.delete_item(**x),
        'GET_COLLECTION': lambda x: dynamo.scan(**x)
    }

    operation = event.get('operation')
    if not operation:
        raise ValueError('"operation" parameter required')
    if operation in debug_operations:
        return debug_operations[operation](event.get('payload'))
    if operation not in dynamo_operations:
        raise ValueError('Unrecognized operation: {}'.format(operation))

    table_name = 'cafes'
    dynamo = boto3.resource('dynamodb').Table(table_name)

    payload = {}
    if operation in ('GET', 'DELETE'):
        payload = {
            "Key": event.get('payload')
        }
    elif operation == 'PUT':
        payload = {
            "Item": event.get('payload')
        }
    return dynamo_operations[operation](payload)
