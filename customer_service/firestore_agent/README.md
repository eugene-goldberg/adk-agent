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

- **project_id**: The Google Cloud project ID (set to `pickuptruckapp`)
- **database_id**: The Firestore database ID (usually '(default)')
- **credentials_path**: Optional path to service account credentials

## Deployment Requirements

When deploying to Vertex AI Agent Engine, ensure:

1. The service account has the necessary Firestore permissions:
   ```bash
   gcloud projects add-iam-policy-binding pickuptruckapp \
     --member="serviceAccount:service-843958766652@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
     --role="roles/datastore.user"
   ```

2. The `google-cloud-firestore` dependency is included in the deployment requirements:
   ```python
   requirements=[
       "google-cloud-aiplatform[adk,agent_engines]",
       "pydantic-settings==2.8.1",
       "google-cloud-firestore>=2.16.1",
       "requests>=2.31.0",
   ]
   ```

## Test Scripts

- **test_firestore_agent.py**: Tests the basic initialization and configuration of the Firestore agent
- **test_firestore_live.py**: Tests all CRUD operations against a live Firestore instance
- **test_firestore_direct.py**: Tests the integration between the Customer Service Agent and Firestore

## Example Usage

### Through the Customer Service Agent

The Customer Service agent handles interactions with Firestore seamlessly:

```
User: "Show me all my bookings"
Agent: *Uses the interact_with_firestore tool with query "query:bookings:{}"*

User: "Create a booking for lawn care on May 15th at 2pm"
Agent: *Creates a booking with interact_with_firestore using write:bookings:booking_uuid:{...}*

User: "What's the status of my May 15th booking?"
Agent: *Retrieves the booking details with query:bookings:{"filters":[{"field":"date","op":"==","value":"2025-05-15"}]}*
```

### Direct Usage

```python
from customer_service.firestore_agent.agent import FirestoreAgent

# Initialize the agent with pickuptruckapp configuration
agent = FirestoreAgent(project_id="pickuptruckapp")

# Query all bookings
result = await agent.process_query("query:bookings:{}")
print(result)

# Create a new booking
booking_data = {
    "customer_id": "customer123",
    "service": "Lawn Care",
    "date": "2025-05-15",
    "time": "14:00-16:00",
    "status": "confirmed"
}
write_result = await agent.process_query(f"write:bookings:booking_uuid:{json.dumps(booking_data)}")
print(write_result)
```

### Integration with Weather Data

The Customer Service agent can combine Firestore data with Weather forecasts for intelligent recommendations:

```
User: "Should I reschedule my garden consultation on May 15th based on the weather?"
Agent: *Retrieves booking from Firestore, checks weather forecast for that date, and provides recommendation*
```

## Best Practices

1. Use proper error handling as Firestore operations may fail due to permissions or connection issues
2. Validate user input before constructing Firestore queries
3. For complex queries requiring sorting, create the appropriate Firestore indexes
4. Keep document IDs consistent and meaningful (e.g., "booking_{uuid}" or "customer_{id}")
5. Use the appropriate data types in Firestore documents for easier querying

## Vertex AI Deployment Details

The Firestore agent is deployed as part of the Customer Service agent to Vertex AI Agent Engine with the following resource ID:

```
projects/843958766652/locations/us-central1/reasoningEngines/1818126039411326976
```

To create a session for testing:

```bash
SESSION=$(python -c "import uuid; print(str(uuid.uuid4()))")
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/843958766652/locations/us-central1/reasoningEngines/1818126039411326976/sessions?session_id=$SESSION"
```

To interact with the deployed agent and test Firestore integration:

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/843958766652/locations/us-central1/reasoningEngines/1818126039411326976/sessions/${SESSION}:reason" \
  -d '{
    "messages": [
      {"author": "user", "content": "Show me all my bookings"}
    ],
    "enableOrchestration": true
  }'
```