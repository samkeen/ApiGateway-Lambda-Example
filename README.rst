ApiGateway-Lambda-Example
=========================

Work in progress, ultimate goal is to complete this as an example that

  - leverages API Gateway and is importable as a RAML doc
  - leveraged Lambda for compute and DynamoDb for persistence.
  - Has auth on the API enabled via Cognito
  - All AWS resources behind the API Gateway (Lambda, Dynamo, IAM, ...) will be created via Cloudformation.


Methods
-------

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
