ApiGateway-Lambda-Example
#########################

Work in progress, ultimate goal is to complete this as an example that

  - leverages API Gateway and is importable as a RAML doc
  - leveraged Lambda for compute and DynamoDb for persistence.
  - Has auth on the API enabled via Cognito
  - All AWS resources behind the API Gateway (Lambda, Dynamo, IAM, ...) will be created via Cloudformation.


Methods
*******

Create a Cafe Item::

    PUT  /cafes

    {
        "id": "<UUID>",
        "name": "...",
        ...
    }

Get an existing Cafe::

    GET  /cafes/{uuid}


GET all Cafes::

    GET  /cafes

Delete a Cafe Item::

    DELETE /cafes/{uuid}

Update a Cafe item::

    GET then edit, then PUT


Cognito Notes
*************

Request/Responses::

     # ===================================
     # Get OpenIdConnect token for the Developer supplied unique user id
     # ===================================
     response = cognito.get_open_id_token_for_developer_identity(
                IdentityPoolId='<AWS REGION>:<POOL_UUID>',
                Logins={
                    'serverless-demo.qstratus.com': user_item['username']
                }
        )

     # Response
     {
       u'Token': u'eyJraWQiOiJ1cy1lYXN~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~BM1Ug',
       'ResponseMetadata': {
         'HTTPStatusCode': 200,
         'RequestId': '<REQUEST_ID_UUID>'},
       u'IdentityId': u'<AWS REGION>:<IDENTITY_ID_UUID>'
     }

     # where 'Token' is the OpenIdConnect Token

     # ===================================
     # Now exchange your OpenIdConnect token for assumed IAM role
     # ===================================
     identity = cognito.get_credentials_for_identity(
                 IdentityId=response['IdentityId'],
                 Logins={
                     'cognito-identity.amazonaws.com': response['Token']
                 }
             )

     # Response
     {
       u'Credentials': {
         u'SecretKey': u'iSNWu2Ddw~~~~~~~~~~~~~~~~~~~~Q3vwUj',
         u'SessionToken': u'AQoDYXdz~~~~~~~~~~~~~~~~~~~~~~~~~~+iCDCnrS1BQ==',
         u'Expiration': datetime.datetime(2016, 1, 30, 20, 30, 10, tzinfo=tzlocal()),
         u'AccessKeyId': u'ASIAJ~~~~~~~~~~~~~~QEA'
       },
       'ResponseMetadata': {
         'HTTPStatusCode': 200,
         'RequestId': '<REQUEST_ID_UUID>'
       },
       u'IdentityId': u'<AWS REGION>:<IDENTITY_ID_UUID>'
     }

Lambda Notes
************

Login Test Payload::

    {
        "resource": "auth",
        "operation": "login",
        "payload": {
            "username": "bob",
            "password": "secret"
        }
    }

Get User Test Payload::

    {
        "resource": "cafe",
        "operation":"GET",
        "payload": {
            "id": "99"
        }
    }
