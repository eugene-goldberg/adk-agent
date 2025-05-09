# Truck Sharing Agent Deployment Guide

This document provides information about the deployed Truck Sharing Agent and how to interact with it.

## Deployment Status

✅ **FULLY DEPLOYED** - The Truck Sharing Agent has been successfully deployed to Google Vertex AI Agent Engine and is fully integrated with the Firestore database. The agent is now available for testing and integration with the PickupTruck mobile app.

## Technical Details

### Environment
- **Python Version**: 3.12.10
- **Vertex AI SDK Version**: 1.92.0
- **Google ADK Version**: 0.2.0
- **Deployment Date**: May 2025
- **Dependencies**:
  - google-cloud-aiplatform[adk,agent_engines]==1.92.0
  - pydantic-settings==2.8.1  
  - google-cloud-firestore>=2.16.1
  - requests>=2.31.0

### Agent Details
- **Project ID**: pickuptruckapp
- **Location**: us-central1
- **Agent Engine ID**: 1369314189046185984 (updated May 2025)
- **Display Name**: truck-sharing-agent
- **Description**: A truck sharing assistant that helps customers book trucks, manage reservations, find suitable vehicles, and check weather conditions for moves.

### Active Sessions
- **Session ID**: 3587306768956391424
- **User ID**: test_user

## Verified Capabilities

The following capabilities have been extensively tested and confirmed working:

1. ✅ **Conversational Interface**: The agent can handle natural language conversations about truck bookings, scheduling, and inquiries.
2. ✅ **Firestore Integration**: The agent is fully integrated with the Firestore database, enabling it to:
   - Query existing customer profiles
   - Search for available vehicles based on criteria (type, availability)
   - Create, read, update, and delete bookings
   - Handle complex booking workflows
3. ✅ **Weather Information**: The agent can provide weather forecasts for moving dates to help customers plan.
4. ✅ **End-to-End Booking**: The agent can guide users through the complete booking process, from inquiry to confirmation.

## Live Bookings in Firestore

The agent has been confirmed to successfully create real bookings in the Firestore database. Current test bookings:

1. **booking_1746726299**: Ford F-150, Status: confirmed
2. **booking_1746726517**: Ford F-150, Status: confirmed

These bookings were created through our testing process and demonstrate the agent's ability to interact with the production database.

## Testing the Agent

There are multiple ways to test and interact with the deployed agent:

### 1. Google Cloud Console (Recommended)

The simplest way to test the agent is through the Google Cloud Console:

1. Visit the following URL to access the agent test page:
   [Agent Test Console](https://console.cloud.google.com/vertex-ai/generative/reasoning-engines/details/9202903528392097792/test?project=pickuptruckapp)

2. You can create a new session or use the existing session ID: `3587306768956391424`

3. Example queries to try:
   - "I need a pickup truck to move some furniture from downtown to my new apartment this Saturday."
   - "What's the weather forecast for my move on Saturday?"
   - "Can I find a truck with a covered bed in case it rains?"
   - "How much would it cost to rent a medium-sized truck for 4 hours?"

### 2. Using the Python Test Scripts

We've developed several Python scripts to test different aspects of the agent:

```bash
# Activate the Python environment
cd /Users/eugene/dev/ai/pickuptruckapp/deploy-adk-agent-engine
source venv-py312/bin/activate

# Test conversation scenarios (simulated, doesn't create real bookings)
python customer_service/test_truck_conversation.py --scenario booking
python customer_service/test_truck_conversation.py --scenario weather

# Test Firestore integration (creates test data then cleans it up)
python customer_service/test_truck_firestore.py

# Create a sample booking in Firestore
python create_sample_booking.py

# Run a full conversation that creates a real booking
python interactive_booking_test.py

# Simple CLI tool to get testing links
python simple_test_cli.py "Your message here"
```

### 3. Integration with Mobile App

For integration with the PickupTruck mobile app, you should use the Google Cloud API to interact with the agent through Vertex AI Agent Engine:

```javascript
// Example React Native frontend integration (conceptual)
import { VertexAI } from '@google-cloud/vertexai';

// Initialize the Vertex AI client
const vertexAI = new VertexAI({
  project: 'pickuptruckapp',
  location: 'us-central1',
});

// Get the agent
const agent = vertexAI.getAgent('9202903528392097792');

// Create a session for a specific user
const session = await agent.createSession(userId);

// Send messages to the agent
const response = await agent.sendMessage(sessionId, 'I need a truck for moving this weekend');

// Display the response to the user
// ...
```

## Code Assets

The following code assets are available for integration:

1. **Conversation Tests**: `customer_service/test_truck_conversation.py` - Test different conversation scenarios
2. **Firestore Integration Tests**: `customer_service/test_truck_firestore.py` - Test database interactions
3. **Interactive Booking Test**: `interactive_booking_test.py` - Create real bookings through simulated conversations
4. **Deployment Scripts**: `deployment/truck_sharing_remote.py` - Update and manage the deployed agent

## Integration Guide

To integrate the agent with the PickupTruck mobile app:

1. **Authentication**: Ensure the mobile app has proper authentication with Google Cloud.
2. **Session Management**: Create and maintain sessions for each user.
3. **Message Handling**: Send user messages to the agent and display responses.
4. **Booking Confirmation**: After a booking is created, fetch and display the booking details.
5. **Error Handling**: Implement proper error handling for network issues or agent unavailability.

## Troubleshooting

If you encounter issues with the agent:

1. **Check Agent Status**: Verify the agent is deployed by visiting the [Reasoning Engines page](https://console.cloud.google.com/vertex-ai/generative/reasoning-engines?project=pickuptruckapp).

2. **Session Issues**: If a session becomes unresponsive, create a new one using:
   ```python
   session = agent.create_session(user_id="user_123")
   ```

3. **Database Connection**: If the agent can't access the database, check the Firestore permissions and ensure the service account has proper access.

4. **Log Analysis**: Check the logs in Google Cloud Console for specific error messages.

## Agent Capabilities

The Truck Sharing Agent provides these key capabilities:

- 🚚 **Vehicle Search**: Find suitable trucks based on requirements
- 💰 **Pricing Information**: Provide accurate price quotes including assistance options
- 🌦️ **Weather Forecasts**: Check weather conditions for moving dates
- 📅 **Booking Management**: Create, view, update, and cancel bookings
- ❓ **Service Information**: Answer questions about the truck sharing service
- 👤 **Customer Profiles**: Access and manage customer information

## Next Steps

1. ✅ ~~Deploy the agent to Vertex AI Agent Engine~~ COMPLETED
2. ✅ ~~Test database integration~~ COMPLETED
3. ✅ ~~Create real bookings through the agent~~ COMPLETED
4. 🔄 Integrate the agent with the PickupTruck mobile app
5. 🔄 Implement user authentication flow for secure bookings
6. 🔄 Add payment processing integration
7. 🔄 Develop feedback collection mechanism
8. 🔄 Implement analytics to track agent performance

## Additional Resources

- [Vertex AI Agent Development Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development)
- [Reasoning Engines Overview](https://cloud.google.com/vertex-ai/generative-ai/docs/reasoning-engines)
- [Google ADK Documentation](https://cloud.google.com/python/docs/reference/aiplatform/latest/vertexai.preview.adk)
- [Firestore Documentation](https://cloud.google.com/firestore/docs)