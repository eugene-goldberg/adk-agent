# TruckBuddy Agent Web Interface

This is a Flask web application that provides a chat interface for interacting with the TruckBuddy Pickup Truck Sharing Agent deployed on Vertex AI.

## Technical Details

### Environment
- **Python Version**: 3.12.10
- **Flask Version**: 2.0.0+
- **Vertex AI SDK Version**: 1.92.0
- **Google ADK Version**: 0.2.0
- **Last Updated**: May 2025
- **Key Dependencies**:
  - google-cloud-aiplatform[adk,agent_engines]==1.92.0
  - pydantic-settings==2.8.1
  - google-cloud-firestore>=2.16.1
  - flask>=2.0.0
  - requests>=2.31.0
  - python-dotenv>=1.0.0

### Deployment Details
- **Project ID**: pickuptruckapp
- **Location**: us-central1
- **Truck Agent Engine ID**: 1369314189046185984 (updated May 2025)
- **API Communication**: Uses direct REST API with streamQuery endpoint

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
- **Truck Sharing Interface**: http://localhost:5000/truck-sharing

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
      "id": "9202903528392097792",
      "resource_id": "projects/pickuptruckapp/locations/us-central1/reasoningEngines/9202903528392097792",
      "display_name": "truck-sharing-agent",
      "description": "A pickup truck sharing assistant that helps customers book trucks, find suitable vehicles for their needs, get weather information for moving dates, and manage their bookings",
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
  "message": "Hello, I need to rent a pickup truck for moving this weekend. What options do you have available?"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Hello! I'd be happy to help you find a pickup truck for your move. We have several options available this weekend...",
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
      "message_sent": "Hello, I need a pickup truck this weekend for moving some furniture. What options do you have?",
      "response": "I can help you find a pickup truck for your move. We have several options available this weekend...",
      "success": true
    },
    "weather": {
      "message_sent": "I need to move next Saturday. What will the weather be like in Boston, and would you recommend an open-bed truck or one with a covered bed?",
      "response": "I checked the forecast for next Saturday in Boston. It looks like there's a 60% chance of rain...",
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

### Mock Mode

For reliable testing without a live deployed agent, the web app provides mock responses for all truck-related features:

1. Set environment variable to enable mock mode:
```bash
export MOCK_AGENT=true
```

2. The web app will generate appropriate truck-themed responses based on the message content, including:
   - Truck information and availability
   - Weather forecasts for moving dates
   - Truck options and add-ons
   - Booking functionality
   - Firestore integration

This allows for testing the full interface even when the Vertex AI deployment is not available or when you want to avoid incurring API costs.

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