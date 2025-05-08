# Truck Sharing Agent Integration Guide

This document provides instructions for integrating the truck sharing AI agent with the mobile app, running tests, and understanding the communication between components.

## Overview

The integration consists of two main components:

1. **NavigationExample (React Native Mobile App)**:
   - A pickup truck sharing service mobile app
   - Uses Firebase Authentication and Firestore
   - Handles UI, user interactions, and direct database operations

2. **Agent Engine (ADK-based Agents)**:
   - AI agents built with Google's Agent Development Kit
   - Deployed on Vertex AI Agent Engine
   - Provides natural language processing for customer interactions
   - Connects to the same Firestore database as the mobile app

## Setup Requirements

Before running tests or deploying the integration, ensure you have:

1. **Google Cloud CLI and Authentication**:
   ```bash
   gcloud auth login
   gcloud config set project pickuptruckapp
   gcloud auth application-default set-quota-project pickuptruckapp
   ```

2. **Python Environment**:
   ```bash
   cd deploy-adk-agent-engine
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Firebase CLI** (for mobile app testing):
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

## Testing the Integration

### 1. Test Firestore Agent Integration

This test verifies that the agent can correctly interact with the Firestore database using the truck app's schema:

```bash
cd deploy-adk-agent-engine
python customer_service/test_truck_firestore.py
```

This script will:
- Create test documents in the users, vehicles, and bookings collections
- Query and update the documents to simulate real operations
- Clean up by deleting the test documents

### 2. Interactive Conversation Test

Test the agent's conversational abilities with simulated user interactions:

```bash
cd deploy-adk-agent-engine
python customer_service/test_truck_conversation.py
```

You can also run specific test scenarios:

```bash
# Test booking flow
python customer_service/test_truck_conversation.py --scenario booking

# Test weather-related queries
python customer_service/test_truck_conversation.py --scenario weather

# Test booking management
python customer_service/test_truck_conversation.py --scenario booking_status

# Run a scenario and then continue interactively
python customer_service/test_truck_conversation.py --scenario booking --interactive
```

## Deploying the Agent

### Local Deployment (Testing)

For local testing of the truck sharing agent:

```bash
cd deploy-adk-agent-engine
python deployment/customer_service_local.py --create_session
python deployment/customer_service_local.py --send --session_id=your-session-id --message="I need to book a truck for this weekend"
```

### Remote Deployment (Production)

To deploy the agent to Vertex AI Agent Engine:

```bash
cd deploy-adk-agent-engine
python deployment/customer_service_remote.py --create
```

After creation, you can set up a session and interact with it:

```bash
python deployment/customer_service_remote.py --create_session --resource_id=your-resource-id
python deployment/customer_service_remote.py --send --resource_id=your-resource-id --session_id=your-session-id --message="Help me book a truck"
```

## Integration with the Mobile App

### API Endpoint for Agent Communication

To enable the mobile app to communicate with the agent, you'll need to set up an API endpoint. The simplest approach is to use Cloud Functions:

1. **Create a Cloud Function in the `functions` directory**:

```python
# This would go in a new file like functions/agent_interface.py
from flask import Flask, request, jsonify
from google.cloud import aiplatform
import google.auth
import os
import json

app = Flask(__name__)

@app.route('/ask-agent', methods=['POST'])
def ask_agent():
    data = request.get_json()
    
    if not data or 'message' not in data or 'user_id' not in data:
        return jsonify({'error': 'Missing required fields: message and user_id'}), 400
    
    # Get parameters
    message = data['message']
    user_id = data['user_id']
    session_id = data.get('session_id')
    
    try:
        # Initialize the Vertex AI SDK
        credentials, project_id = google.auth.default()
        aiplatform.init(project=project_id, location="us-central1")
        
        # Get or create agent session
        if not session_id:
            # Create a new session
            agent_endpoint = aiplatform.Publisher.get(
                resource_name=f"projects/{project_id}/locations/us-central1/publishers/google/agents/truck-sharing-agent"
            )
            session = agent_endpoint.create_session()
            session_id = session.name
        else:
            # Use existing session
            session = aiplatform.PublisherSession(name=session_id)
        
        # Send message to agent
        response = session.send_message(message)
        
        return jsonify({
            'response': response.text,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
```

2. **Call the Agent API from the mobile app**:

Add a service in the mobile app to handle agent communication:

```typescript
// services/agent-service.ts

import axios from 'axios';

const API_URL = 'https://your-cloud-function-url.com/ask-agent';

export interface AgentResponse {
  response: string;
  session_id: string;
}

export const sendMessageToAgent = async (
  message: string,
  userId: string,
  sessionId?: string
): Promise<AgentResponse> => {
  try {
    const response = await axios.post(API_URL, {
      message,
      user_id: userId,
      session_id: sessionId
    });
    
    return response.data;
  } catch (error) {
    console.error('Error sending message to agent:', error);
    throw error;
  }
};

export const startNewAgentSession = async (
  userId: string
): Promise<string> => {
  // Send an initial greeting to create a new session
  const response = await sendMessageToAgent('Hello', userId);
  return response.session_id;
};
```

3. **Create a Chat UI in the mobile app**:

Add a chat screen to the mobile app that uses the agent service:

```typescript
// app/agent-chat.tsx

import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { sendMessageToAgent } from '../services/agent-service';

export default function AgentChatScreen() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<{text: string, sender: 'user' | 'agent'}[]>([]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Initialize with a greeting from the agent
    handleInitialGreeting();
  }, []);

  const handleInitialGreeting = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      const response = await sendMessageToAgent('Hello', user.uid);
      setSessionId(response.session_id);
      setMessages([{ text: response.response, sender: 'agent' }]);
    } catch (error) {
      console.error('Error getting initial greeting:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() || !user) return;
    
    const userMessage = inputText.trim();
    setInputText('');
    
    // Add user message to the chat
    setMessages(prevMessages => [...prevMessages, { text: userMessage, sender: 'user' }]);
    
    setIsLoading(true);
    try {
      const response = await sendMessageToAgent(userMessage, user.uid, sessionId || undefined);
      
      // Update session ID if it's a new session
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
      }
      
      // Add agent response to the chat
      setMessages(prevMessages => [...prevMessages, { text: response.response, sender: 'agent' }]);
    } catch (error) {
      console.error('Error sending message to agent:', error);
      setMessages(prevMessages => [
        ...prevMessages, 
        { text: 'Sorry, I encountered an error. Please try again.', sender: 'agent' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.messagesContainer}>
        {messages.map((message, index) => (
          <View 
            key={index} 
            style={[
              styles.messageBubble, 
              message.sender === 'user' ? styles.userMessage : styles.agentMessage
            ]}
          >
            <Text style={styles.messageText}>{message.text}</Text>
          </View>
        ))}
        {isLoading && (
          <View style={[styles.messageBubble, styles.agentMessage]}>
            <Text style={styles.messageText}>Typing...</Text>
          </View>
        )}
      </ScrollView>
      
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Type your message..."
          placeholderTextColor="#999"
          multiline
        />
        <TouchableOpacity 
          style={styles.sendButton} 
          onPress={handleSendMessage}
          disabled={!inputText.trim() || isLoading}
        >
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  messagesContainer: {
    flex: 1,
    padding: 10,
  },
  messageBubble: {
    padding: 10,
    borderRadius: 20,
    marginVertical: 5,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  agentMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#E5E5EA',
  },
  messageText: {
    fontSize: 16,
    color: '#000',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#E5E5EA',
  },
  input: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    borderRadius: 20,
    paddingHorizontal: 15,
    paddingVertical: 10,
    maxHeight: 100,
  },
  sendButton: {
    marginLeft: 10,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
    width: 60,
    borderRadius: 20,
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});
```

## Data Flow in the Integrated System

1. **User Interaction**:
   - User interacts with the mobile app UI
   - They can navigate to the Agent Chat screen for NLP-based interaction
   - They can also use the regular app UI for direct actions

2. **Agent Processing**:
   - User messages are sent to the agent via the Cloud Function
   - Agent processes the request and may use its tools to:
     - Get information from Firestore
     - Update/create records in Firestore
     - Get weather information
     - Facilitate video connections

3. **Database Operations**:
   - Both the mobile app and agent read/write to the same Firestore database
   - Changes made by either component are immediately visible to the other
   - The mobile app can react to database changes triggered by the agent

4. **Synchronization**:
   - The mobile app should include a listener for relevant Firestore collections
   - When the agent creates a booking, the app UI should update automatically
   - Similarly, when a user makes changes through the app UI, the agent has access to the updated information

## Common Integration Patterns

### 1. Booking Creation

**Through Agent**:
1. User describes their booking needs in natural language
2. Agent extracts necessary information and creates a booking record
3. Mobile app detects the new booking and updates the UI
4. User can view/modify the booking through the regular app UI

**Through App UI**:
1. User fills out booking form in the app
2. App creates a booking record directly
3. Agent can access this booking during future conversations

### 2. Booking Management

**Viewing Bookings**:
- Agent can retrieve and summarize booking information
- App displays detailed booking views and status updates

**Modifying Bookings**:
- Both agent and app UI can update booking status, times, etc.
- Changes are synchronized through Firestore

### 3. Vehicle Discovery

**Through Agent**:
- Natural language queries to find appropriate vehicles
- Agent uses Firestore queries to find matching vehicles
- Agent explains vehicle features and benefits conversationally

**Through App UI**:
- Structured search filters and sorting options
- Grid/list views with vehicle cards
- Detailed vehicle information pages

## Troubleshooting

### Agent Not Responding
- Check that the agent is properly deployed on Vertex AI
- Verify the Cloud Function can access the agent
- Check authentication credentials and permissions

### Database Sync Issues
- Ensure both the app and agent are using the same Firestore instance
- Check security rules to ensure proper access permissions
- Verify the schema matches what each component expects

### Performance Considerations
- For high-traffic applications, consider implementing caching for agent responses
- Use pagination when querying large collections
- Consider implementing webhook notifications for important state changes