# Agent Integration Notes

## Overview

This document explains how to properly interact with Vertex AI agents deployed using the Agent Development Kit (ADK). The solution presented here resolves compatibility issues between different versions of the Vertex AI SDK.

## Environment Details

1. **Python Version**: 3.12.10
2. **Vertex AI SDK Version**: 1.92.0
3. **ADK Version**: 0.2.0
4. **Deployment Date**: May 2025
5. **Dependencies**:
   - google-cloud-aiplatform[adk,agent_engines]==1.92.0
   - google-adk>=0.2.0
   - pydantic>=2.0.0
   - pydantic-settings==2.8.1
   - google-cloud-firestore>=2.16.1
   - requests>=2.31.0
   - python-dotenv>=1.0.0

## Key Components

1. **Deployed Agents**:
   - Truck Sharing Agent: `projects/843958766652/locations/us-central1/reasoningEngines/1369314189046185984`
   - Customer Service Agent: `projects/843958766652/locations/us-central1/reasoningEngines/2753748861997547520`

2. **API Approach**:
   - We use the direct REST API call to the `:streamQuery` endpoint
   - HTTP Method: POST
   - Endpoint format: `https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/reasoningEngines/{resource_id}:streamQuery`

## Session Management

Sessions must be created before sending messages. The session creation process works with the standard Python SDK approach:

```python
remote_app = agent_engines.get(resource_id)
session = remote_app.create_session(user_id="test_user")
session_id = session.get('id')  # For dict-like session object
# OR
session_id = session.id  # For object-like session object
```

## Sending Messages

The correct approach to send messages to the agent is a direct REST API call to the `:streamQuery` endpoint:

```python
import requests
import google.auth
import google.auth.transport.requests

# Get credentials
credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
token = credentials.token

# Construct the API endpoint
endpoint = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/reasoningEngines/{resource_id}:streamQuery"

# Prepare the request payload
payload = {
    "class_method": "stream_query",
    "input": {
        "user_id": "test_user",
        "session_id": session_id,
        "message": message
    }
}

# Set headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Send the request
response = requests.post(endpoint, headers=headers, json=payload, timeout=45)
```

## Handling the Response

The response from the `:streamQuery` endpoint is a series of JSON objects that may be separated by newlines. The proper way to handle this is:

```python
# The response may be a series of JSON objects separated by newlines
raw_response = response.text

# Try to extract the relevant response info
content = None
try:
    # Try parsing the response as a complete JSON object
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        content = result[-1]  # Last object is usually the final response
    else:
        content = result
except json.JSONDecodeError:
    # Try parsing line by line for streaming responses
    try:
        lines = raw_response.strip().split('\n')
        # Parse the last complete JSON object from the response
        for line in reversed(lines):
            if line.strip():
                content = json.loads(line)
                break
    except json.JSONDecodeError:
        # If we can't parse the JSON, just use the text
        content = {"text": raw_response}

# Extract the message text
response_text = ""
if content:
    if "content" in content and "parts" in content["content"]:
        for part in content["content"]["parts"]:
            if "text" in part:
                response_text += part["text"]
    elif "text" in content:
        response_text = content["text"]
```

## Key Discoveries

1. **SDK Version Compatibility**:
   - Previous deployments used SDK version 1.89.0
   - Updated deployments use SDK version 1.92.0
   - The SDK API interfaces changed between these versions

2. **API Endpoint Changes**:
   - The `:query` endpoint doesn't work for message sending
   - The `:streamQuery` endpoint is required
   - The API requires specific formatting of the payload

3. **Available Methods**:
   - Our deployment supports these methods: `delete_session`, `list_sessions`, `create_session`, `get_session`
   - It does not directly expose `query` or `stream_query` methods via the Python SDK

## Error Handling Recommendations

1. For HTTP 400 errors: Check that the payload format is correct
2. For HTTP 404 errors: Verify that the resource ID and session ID are valid
3. For HTTP 429 errors: Implement rate limiting or exponential backoff 
4. For parsing errors: Implement fallback mechanisms for response formats

## Deployment Process

When redeploying agents, follow these steps:

1. Delete existing deployments:
   ```
   python deployment/truck_sharing_remote.py --delete --resource_id=<resource_id>
   ```

2. Deploy with the latest SDK:
   ```
   python deployment/truck_sharing_remote.py --create
   ```

3. Update the resource ID constants in the application:
   ```python
   DEFAULT_RESOURCE_ID = "<new_resource_id>"
   ```

## Testing Agents Independently

The repository includes a test script that demonstrates successful agent communication:
```
python test_truck_sharing_agent.py
```

This script demonstrates the working API approach and can be used for troubleshooting.

## Future Recommendations

1. Consider implementing a proper client library that abstracts the API interactions
2. Add comprehensive error handling and retries for better resilience
3. Implement proper rate limiting to avoid quota issues
4. Add detailed logging for debugging API interactions
5. Implement a fallback mechanism for when the API is unavailable