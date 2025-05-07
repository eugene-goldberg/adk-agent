# Firestore Agent for Customer Service

This module integrates Google Firestore with the Customer Service Agent, enabling data persistence and retrieval for customer bookings and information.

## Features

- **Sub-agent Architecture**: Implemented as a sub-agent of the main Customer Service Agent
- **CRUD Operations**: Complete support for Create, Read, Update, Delete operations
- **Query Capabilities**: Filtering, sorting, and limiting results
- **Date Formatting**: Proper handling of Firestore datetime objects
- **Error Handling**: Graceful handling of permission issues and invalid queries
- **Flexible Integration**: Can be used directly or through the Customer Service Agent

## Architecture

The Firestore integration consists of three main components:

1. **FirestoreAgent Class (`agent.py`)**: Main agent that handles operations through a query interface
2. **Database Operations (`tools.py`)**: Functions for interacting with Firestore
3. **Integration Tool (`customer_service/tools/tools.py`)**: The `interact_with_firestore` function that makes the Firestore agent available to the Customer Service Agent

## Query Interface

The Firestore agent uses a string-based query interface with the following format:
```
operation:collection_name:document_id:data
```

### Supported Operations

- **read**: Read a document
  ```
  read:customers:customer123
  ```

- **write**: Write a new document
  ```
  write:bookings:booking123:{"customer_id":"123","date":"2025-05-25","time":"9-12"}
  ```

- **update**: Update an existing document
  ```
  update:bookings:booking456:{"status":"confirmed","notes":"Updated booking"}
  ```

- **delete**: Delete a document
  ```
  delete:bookings:booking789
  ```

- **query**: Query a collection
  ```
  query:bookings:{}
  ```
  
  With filtering and sorting:
  ```
  query:bookings:{"filters":[{"field":"status","op":"==","value":"confirmed"}],"limit":10,"order_by":"date"}
  ```

## Configuration

Configuration is handled through the main `Config` class in `customer_service/config.py`. The Firestore settings include:

- **project_id**: The Google Cloud project ID
- **database_id**: The Firestore database ID (usually 'default')
- **credentials_path**: Optional path to service account credentials

## Deployment Requirements

When deploying to Vertex AI Agent Engine, ensure:

1. The service account has the necessary Firestore permissions:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:service-YOUR_PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
     --role="roles/datastore.user"
   ```

2. Include the `google-cloud-firestore` dependency in the deployment requirements.

## Test Scripts

- **test_firestore_agent.py**: Tests the basic initialization and configuration of the Firestore agent
- **test_firestore_live.py**: Tests all CRUD operations against a live Firestore instance
- **test_firestore_direct.py**: Tests the integration between the Customer Service Agent and Firestore

## Example Usage

### Through the Customer Service Agent

```
User: "Show me all my bookings"
Agent: *Uses the interact_with_firestore tool with query "query:bookings:{}"*
```

### Direct Usage

```python
from customer_service.firestore_agent.agent import FirestoreAgent

agent = FirestoreAgent()
result = await agent.process_query("query:bookings:{}")
print(result)
```

## Best Practices

1. Use proper error handling as Firestore operations may fail due to permissions or connection issues
2. Validate user input before constructing Firestore queries
3. For complex queries requiring sorting, create the appropriate Firestore indexes
4. Keep document IDs consistent and meaningful (e.g., "booking_{uuid}" or "customer_{id}")
5. Use the appropriate data types in Firestore documents for easier querying