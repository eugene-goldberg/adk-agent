# Customer Service Agent Web Interface

This is a Flask web application that provides a chat interface for interacting with the Cymbal Home & Garden Customer Service Agent deployed on Vertex AI.

## Features

- Chat interface for communicating with the deployed agent
- Session management for maintaining conversation state
- AJAX-based API for seamless interactions
- Ability to create new sessions
- Agent discovery interface to find and test deployed agents
- API testing interface for directly interacting with all endpoints
- Feature testing capabilities to validate agent functionality
- Loading indicators during agent communication
- Responsive design that works on desktop and mobile
- Authentication using Google Cloud credentials

## Setup

### Prerequisites

- Python 3.9+
- Google Cloud SDK installed and configured
- Vertex AI agent deployed (Resource ID available)
- Google Cloud Application Default Credentials configured

### Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set environment variables (create a `.env` file in the project root or use existing one):

```
GOOGLE_CLOUD_PROJECT=pickuptruckapp
GOOGLE_CLOUD_LOCATION=us-central1
AGENT_RESOURCE_ID=1818126039411326976
```

3. Ensure you're authenticated with Google Cloud:

```bash
gcloud auth login
gcloud auth application-default set-quota-project pickuptruckapp
```

## Running the Web App

To run the web application locally:

```bash
cd web_app
python app.py
```

The application will be available at http://localhost:5000/

If port 5000 is already in use (common on macOS where AirPlay uses this port), you can specify an alternative port:

```bash
python app.py --port=5001
```

### Available Pages

- **Main Chat Interface**: http://localhost:5000/ (or your specified port)
- **Agent Discovery Interface**: http://localhost:5000/agent-discovery
- **Agent Testing Interface**: http://localhost:5000/agent-testing

## API Endpoints

The application provides the following RESTful API endpoints:

### Chat Session API

#### Create a new session

**Request:**
```
POST /api/sessions
```

**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid"
}
```

#### Send a message

**Request:**
```
POST /api/sessions/{session_id}/messages

{
  "message": "Your message text here"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Agent's response text"
}
```

#### Get messages for a session

**Request:**
```
GET /api/sessions/{session_id}/messages
```

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "author": "user",
      "content": "User message"
    },
    {
      "author": "agent",
      "content": "Agent response"
    }
  ]
}
```

### Agent Discovery API

The Agent Discovery API provides endpoints for discovering, creating sessions, and testing deployed agents on Vertex AI.

#### Discover agents

**Request:**
```
GET /api/discovery/discover
```

**Response:**
```json
{
  "success": true,
  "agents": [
    {
      "id": "1818126039411326976",
      "resource_id": "projects/pickuptruckapp/locations/us-central1/reasoningEngines/1818126039411326976",
      "display_name": "customer-service-agent",
      "description": "A customer service agent for Cymbal Home & Garden",
      "created": "2025-05-08T14:22:10.990577Z",
      "updated": "2025-05-08T14:24:36.339561Z",
      "python_version": "3.12"
    }
  ]
}
```

#### Create a session with an agent

**Request:**
```
POST /api/discovery/create_session

{
  "resource_id": "1818126039411326976",
  "name": "Test Session"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "3922824941195493376",
  "resource_id": "1818126039411326976",
  "uuid": "eff77ffa-9a7d-4615-a6f3-20ebfd8786d5",
  "name": "Test Session"
}
```

#### List saved sessions

**Request:**
```
GET /api/discovery/sessions
```

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "created": "2025-05-08T10:46:35.137456",
      "last_used": 1746719195.137482,
      "name": "Test Session",
      "resource_id": "1818126039411326976",
      "session_id": "3922824941195493376",
      "timestamp": 1746719195.137482,
      "uuid": "eff77ffa-9a7d-4615-a6f3-20ebfd8786d5"
    }
  ]
}
```

#### Send a message to an agent

**Request:**
```
POST /api/discovery/send_message

{
  "session_uuid": "eff77ffa-9a7d-4615-a6f3-20ebfd8786d5",
  "message": "Hello, can you help me with gardening advice?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Hello! I'd be happy to help with gardening advice...",
  "session_id": "3922824941195493376",
  "resource_id": "1818126039411326976"
}
```

#### Test agent features

**Request:**
```
POST /api/discovery/test_features

{
  "session_uuid": "eff77ffa-9a7d-4615-a6f3-20ebfd8786d5",
  "features": ["basic", "weather"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "basic": {
      "message_sent": "Hello, I'm looking for recommendations for plants that would do well in a desert climate.",
      "response": "I can definitely help with that! Desert plants need to be drought-resistant...",
      "success": true
    },
    "weather": {
      "message_sent": "What's the weather going to be like in Las Vegas this week?",
      "response": "The weather in Las Vegas is going to be sunny for the next few days...",
      "success": true
    }
  },
  "session_id": "3922824941195493376",
  "resource_id": "1818126039411326976"
}
```

## Testing the API

The web app includes a test script for validating the API endpoints. To run the tests:

```bash
cd web_app
python test_api.py
```

For verbose output with detailed request/response information:

```bash
python test_api.py --verbose
```

To interactively chat with the agent through the API:

```bash
python test_api.py --interactive
```

## Usage

### Chat Interface

1. When you first visit the web app, it will automatically create a new session.
2. Type your message in the input field and click "Send" to communicate with the agent.
3. The conversation history will be displayed in the chat window.
4. To start a new conversation, click the "New Session" button.

### Agent Discovery Interface

The Agent Discovery interface is available at `/agent-discovery` and provides:

1. **API Testing Section**: 
   - Direct testing of all 5 API endpoints with input forms
   - JSON response display for each endpoint
   - Ability to test endpoints in sequence with auto-filled values

2. **Interactive Agent UI**:
   - Discover deployed agents on Vertex AI
   - Create and manage sessions
   - Send messages to agents
   - Run feature tests to verify agent capabilities

To use the Agent Discovery interface:

1. Click "Test Discover Endpoint" to find available agents
2. Create a session using the discovered agent ID
3. Use the session UUID to send messages or run feature tests
4. View detailed JSON responses for all API calls

## How It Works

1. The application creates a session with the Vertex AI agent when you first visit the page.
2. When you send a message, it's forwarded to the deployed agent through the Vertex AI API.
3. The agent's response is displayed in the chat window.
4. All communication happens via AJAX calls to prevent page reloads.
5. The conversation history is maintained in the Flask session.

## Troubleshooting

If you encounter issues:

1. Ensure your Google Cloud credentials are valid and have the necessary permissions.
2. Check that the agent resource ID is correct and the agent is deployed.
3. Verify the project ID and location in your environment variables match your deployment.
4. Check browser console and application logs for specific error messages.
5. Use the test_api.py script with --verbose flag to diagnose API issues.

## Extension Points

Current enhancements:
- Agent discovery and testing interface ✅
- API testing interface ✅
- Feature testing capabilities ✅
- Session management with persistent storage ✅
- Response parsing with improved error handling ✅

Future enhancements:
- Add user authentication to support multiple users
- Implement file upload capability for sharing images with the agent
- Add export functionality to save conversation history and test results
- Integrate with the Weather API for real-time weather data
- Add continuous integration tests for agent features
- Create automated test reports and dashboards
- Implement webhook capabilities for agent integration with external services
- Add Swagger/OpenAPI documentation for the API endpoints
- Support multiple agent versions and A/B testing