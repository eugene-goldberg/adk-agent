# PickupTruck Mobile App Integration Guide

This document provides detailed information on how to integrate the deployed Truck Sharing Agent with the PickupTruck React Native mobile application.

## Overview

The Truck Sharing Agent has been successfully deployed to Google Vertex AI Agent Engine and is ready for integration with the mobile app. This guide explains how to:

1. Connect the React Native app to the deployed agent
2. Implement user authentication for secure agent interactions
3. Create and manage user sessions
4. Handle agent conversations in the UI
5. Process booking confirmations

## System Architecture

```
┌─────────────────┐      ┌───────────────────┐      ┌───────────────────┐
│  React Native   │      │   Google Vertex   │      │     Firestore     │
│  Mobile App     │ <--> │   AI Agent Engine │ <--> │     Database      │
└─────────────────┘      └───────────────────┘      └───────────────────┘
```

- **Mobile App**: Handles UI/UX, user authentication, and API calls
- **Agent Engine**: Processes natural language, maintains conversation context, and interacts with database
- **Firestore**: Stores and retrieves user profiles, vehicle data, and bookings

## Required Dependencies

Add these dependencies to your React Native project:

```bash
# Install Google Cloud dependencies
npm install @google-cloud/vertexai
npm install @react-native-firebase/app
npm install @react-native-firebase/firestore
npm install @react-native-firebase/auth

# UI components for chat interface
npm install react-native-gifted-chat
```

## Authentication Setup

### 1. Firebase Authentication

Ensure Firebase Authentication is configured in your app:

```javascript
// firebase.js
import auth from '@react-native-firebase/auth';

export const signIn = async (email, password) => {
  try {
    const userCredential = await auth().signInWithEmailAndPassword(email, password);
    return userCredential.user;
  } catch (error) {
    console.error('Error signing in:', error);
    throw error;
  }
};

export const getCurrentUser = () => {
  return auth().currentUser;
};
```

### 2. Google Cloud Authentication

Set up authentication for Vertex AI:

```javascript
// vertexai.js
import { VertexAI } from '@google-cloud/vertexai';
import auth from '@react-native-firebase/auth';

// Initialize the Vertex AI client
export const initializeVertexAI = async () => {
  // Get Firebase ID token
  const idToken = await auth().currentUser.getIdToken();
  
  return new VertexAI({
    project: 'pickuptruckapp',
    location: 'us-central1',
    googleAuthToken: idToken,
  });
};
```

## Agent Integration

### 1. Agent Service

Create an agent service module:

```javascript
// services/agentService.js
import { initializeVertexAI } from '../vertexai';

const AGENT_ID = '9202903528392097792';

export default class AgentService {
  constructor() {
    this.vertexAI = null;
    this.agent = null;
    this.sessionId = null;
  }

  async initialize() {
    try {
      this.vertexAI = await initializeVertexAI();
      this.agent = this.vertexAI.getAgent(AGENT_ID);
      return true;
    } catch (error) {
      console.error('Error initializing agent service:', error);
      return false;
    }
  }

  async createSession(userId) {
    try {
      const session = await this.agent.createSession(userId);
      this.sessionId = session.id;
      return session;
    } catch (error) {
      console.error('Error creating session:', error);
      throw error;
    }
  }

  async sendMessage(message) {
    if (!this.sessionId) {
      throw new Error('No active session. Call createSession first.');
    }

    try {
      const response = await this.agent.sendMessage(this.sessionId, message);
      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }
}
```

### 2. Chat UI Component

Implement the chat interface:

```javascript
// components/TruckBuddyChat.js
import React, { useState, useEffect, useCallback } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { GiftedChat } from 'react-native-gifted-chat';
import AgentService from '../services/agentService';
import { getCurrentUser } from '../firebase';

const TruckBuddyChat = () => {
  const [messages, setMessages] = useState([]);
  const [agentService, setAgentService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initializeChat = async () => {
      try {
        const service = new AgentService();
        await service.initialize();
        
        const user = getCurrentUser();
        await service.createSession(user.uid);
        
        setAgentService(service);
        
        // Add welcome message
        setMessages([
          {
            _id: 1,
            text: "Hello! I'm TruckBuddy, your assistant for the PickupTruck App. How can I help you today?",
            createdAt: new Date(),
            user: {
              _id: 2,
              name: 'TruckBuddy',
              avatar: require('../assets/truckbuddy-icon.png'),
            },
          },
        ]);
        
        setLoading(false);
      } catch (err) {
        console.error('Error initializing chat:', err);
        setError('Failed to connect to TruckBuddy. Please try again later.');
        setLoading(false);
      }
    };

    initializeChat();
  }, []);

  const onSend = useCallback(async (newMessages = []) => {
    const userMessage = newMessages[0];
    
    // Add user message to chat
    setMessages(previousMessages => 
      GiftedChat.append(previousMessages, userMessage)
    );
    
    // Show typing indicator
    setMessages(previousMessages => 
      GiftedChat.append(previousMessages, {
        _id: Math.random().toString(),
        text: '...',
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'TruckBuddy',
        },
        isTyping: true,
      })
    );
    
    try {
      // Send message to agent
      const response = await agentService.sendMessage(userMessage.text);
      
      // Remove typing indicator and add agent response
      setMessages(previousMessages => {
        // Filter out typing indicator
        const filteredMessages = previousMessages.filter(msg => !msg.isTyping);
        
        // Add agent response
        return GiftedChat.append(filteredMessages, {
          _id: Math.random().toString(),
          text: response.text,
          createdAt: new Date(),
          user: {
            _id: 2,
            name: 'TruckBuddy',
            avatar: require('../assets/truckbuddy-icon.png'),
          },
        });
      });
      
      // Handle booking confirmations
      if (response.data && response.data.booking) {
        // Navigate to booking confirmation screen
        // navigation.navigate('BookingConfirmation', { booking: response.data.booking });
      }
    } catch (err) {
      console.error('Error sending message:', err);
      
      // Remove typing indicator and add error message
      setMessages(previousMessages => {
        const filteredMessages = previousMessages.filter(msg => !msg.isTyping);
        return GiftedChat.append(filteredMessages, {
          _id: Math.random().toString(),
          text: 'Sorry, I encountered an error processing your message. Please try again.',
          createdAt: new Date(),
          user: {
            _id: 2,
            name: 'TruckBuddy',
            avatar: require('../assets/truckbuddy-icon.png'),
          },
        });
      });
    }
  }, [agentService]);

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#0000ff" />
      </View>
    );
  }

  if (error) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <Text style={{ color: 'red' }}>{error}</Text>
      </View>
    );
  }

  return (
    <GiftedChat
      messages={messages}
      onSend={newMessages => onSend(newMessages)}
      user={{
        _id: 1,
      }}
      renderAvatar={null}
      placeholder="Message TruckBuddy..."
    />
  );
};

export default TruckBuddyChat;
```

### 3. Add Chat Screen to Navigation

```javascript
// app/screens/ChatScreen.js
import React from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import TruckBuddyChat from '../../components/TruckBuddyChat';

const ChatScreen = () => {
  return (
    <SafeAreaView style={styles.container}>
      <TruckBuddyChat />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});

export default ChatScreen;
```

## Booking Confirmation Integration

When the agent creates a booking, you need to display the confirmation to the user:

```javascript
// app/screens/BookingConfirmationScreen.js
import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Button } from 'react-native-paper';

const BookingConfirmationScreen = ({ route, navigation }) => {
  const { booking } = route.params;
  
  // Format the date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    });
  };
  
  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Booking Confirmed!</Text>
        <Text style={styles.bookingId}>Booking ID: {booking.id}</Text>
        
        <View style={styles.detailRow}>
          <Text style={styles.label}>Vehicle:</Text>
          <Text style={styles.value}>{booking.vehicleMake} {booking.vehicleModel}</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.label}>Date & Time:</Text>
          <Text style={styles.value}>{formatDate(booking.pickupDateTime)}</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.label}>Duration:</Text>
          <Text style={styles.value}>{booking.estimatedHours} hours</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.label}>Pickup:</Text>
          <Text style={styles.value}>{booking.pickupAddress}</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.label}>Destination:</Text>
          <Text style={styles.value}>{booking.destinationAddress}</Text>
        </View>
        
        <View style={styles.detailRow}>
          <Text style={styles.label}>Assistance:</Text>
          <Text style={styles.value}>{booking.needsAssistance ? 'Yes' : 'No'}</Text>
        </View>
        
        <View style={styles.costSummary}>
          <Text style={styles.label}>Vehicle Cost:</Text>
          <Text style={styles.value}>${booking.truckCost.toFixed(2)}</Text>
          
          {booking.needsAssistance && (
            <>
              <Text style={styles.label}>Assistance:</Text>
              <Text style={styles.value}>${booking.assistanceCost.toFixed(2)}</Text>
            </>
          )}
          
          <Text style={styles.totalLabel}>Total:</Text>
          <Text style={styles.totalValue}>${booking.totalCost.toFixed(2)}</Text>
        </View>
        
        <Button
          mode="contained"
          style={styles.button}
          onPress={() => navigation.navigate('Bookings')}
        >
          View All Bookings
        </Button>
        
        <Button
          mode="outlined"
          style={styles.button}
          onPress={() => navigation.navigate('Home')}
        >
          Back to Home
        </Button>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginVertical: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
    textAlign: 'center',
    color: '#4CAF50',
  },
  bookingId: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    textAlign: 'center',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 8,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  value: {
    fontSize: 16,
    color: '#666',
    flex: 1,
    textAlign: 'right',
  },
  costSummary: {
    marginTop: 16,
    marginBottom: 24,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#ddd',
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000',
    marginTop: 8,
  },
  totalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
    textAlign: 'right',
  },
  button: {
    marginTop: 12,
  },
});

export default BookingConfirmationScreen;
```

## Troubleshooting

### 1. Authentication Issues

If you encounter authentication issues:

- Ensure Firebase authentication is properly set up
- Check that the user is signed in before initializing the agent
- Verify that ID tokens are being correctly generated and sent

### 2. Agent Connection Problems

If the agent doesn't respond:

- Check that the agent ID is correct
- Verify the session was created successfully
- Check network connectivity
- Look for error messages in the console

### 3. Booking Creation Failures

If bookings fail to be created:

- Ensure the agent has proper Firestore permissions
- Check that all required booking fields are being provided in the conversation
- Verify that the vehicle IDs being referenced exist in the database

## Testing

Test the integration thoroughly:

1. **Basic Conversation**: Test simple back-and-forth messages
2. **Booking Flow**: Complete the entire booking process
3. **Error Handling**: Test behavior when network or service is unavailable
4. **Session Management**: Test behavior after app restart or background

## Security Considerations

1. **User Authentication**: Always authenticate users before connecting to the agent
2. **Token Management**: Refresh tokens when needed and handle expiration
3. **Data Validation**: Validate booking data returned from the agent
4. **Error Messages**: Don't expose sensitive information in error messages

## Performance Optimization

1. **Session Caching**: Store session IDs for faster reconnection
2. **Message Batching**: Consider batching messages for better UX
3. **Offline Support**: Implement message queuing for offline mode
4. **Image Compression**: Compress vehicle images for faster loading

## Next Steps

1. **Analytics Integration**: Track conversation quality and conversion rates
2. **Push Notifications**: Implement booking reminders and status updates
3. **User Feedback**: Add rating system for agent interactions
4. **Expanded Capabilities**: Integrate payment processing for bookings

---

## Appendix: API Reference

### Agent Engine API

```javascript
// Create a session
const session = await agent.createSession(userId);
// session.id contains the session ID

// Send a message
const response = await agent.sendMessage(sessionId, message);
// response contains the agent's reply
```

### Firestore API

```javascript
// Get user bookings
const bookingsSnapshot = await firestore()
  .collection('bookings')
  .where('customerId', '==', userId)
  .get();

// Get booking details
const bookingSnapshot = await firestore()
  .collection('bookings')
  .doc(bookingId)
  .get();
```