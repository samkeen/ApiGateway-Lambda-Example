ApiGateway-Lambda-Example
#########################

Work in progress, ultimate goal is to complete this as an example that

  - leverages API Gateway and is importable as a RAML doc
  - leveraged Lambda for compute and DynamoDb for persistence.
  - Has auth on the API enabled via Cognito
  - All AWS resources behind the API Gateway (Lambda, Dynamo, IAM, ...) will be created via Cloudformation.


The Auth Flow
*************

When dealing with Cognito (and web security in general), it is important to know the difference between Authentication
and Authorization.

**Authentication**: Is any process by which a system verifies the identity of a User who wishes to access it. (*Who am I*)

**Authorization**: The function of specifying access rights to resources. (*What can I do*).

You'll see many discussions that skew the meanings of these terms, incorrectly using them interchangeably.  For security
reasons it is important to know the difference and keep these different concerns separate when developing applications.
AWS in general does and excellent job of this (it is the entire basis of Cognito).

With regards to security, a site/service build with the strategy presented here will have two scopes.  An Authenticate
scope (e.g. /login) that a user leverages to prove their identity, in order to link to a set of Authorizations for
your site/service.  The rest of the site is simply the Authenticated scope.  Every request to an endpoint in this
scope requires the request to be *signed* using credentials obtained via the Authenticate scope.

The discrete steps for Authentication/Authorization of this examples are:

0. Create a `Cognito Identity pool <https://docs.aws.amazon.com/cognito/devguide/identity/identity-pools/>`_.  The TL;DR
of Identity pools is that they create a namespace for user Identities; the Pool.  To this pool you attach
Authentication providers, for this example you will have only a custom, *Developer provider* Authentication provider.
Secondly, you attach Authorization permissions to this pool in the form of IAM policies.

1. Authenticate your user as you always would.  Most likely asking for username an password and comparing that to
what you have persisted in a database.

2. With the user's unique Id (email, uuid, ...), obtained in step one, we make a developer credential signed
call to Cognito to generate (or retrieve) the Identity pool's uuid for this user + an expiring OpenIdConnect token for
this user.

3. When then turn around and make an unsigned call to Cognito and exchange the OpenIdConnect token for a set of expiring credentials to pass back to the Client.  These credentials grant the Authorization permissions of the IAM policy associated
with the Cognito Identity Pool to the user we Authenticated in step 1.  The client will then use the credentials to
sign requests for the Authenticated scope of the site/service.

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
