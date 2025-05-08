#!/usr/bin/env python3
"""
Interactive demo chat script for the Cymbal Home & Garden Customer Service Agent.
This script simulates a conversation with the agent without needing a full web server.
"""

import os
import uuid
import json
import time
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

# Mock agent responses based on the actual Cymbal Home & Garden agent
RESPONSES = {
    "greeting": [
        "Welcome to Cymbal Home & Garden! I'm your customer service assistant. How can I help you today?",
        "Hello! I'm the customer service agent for Cymbal Home & Garden. What can I assist you with?",
        "Hi there! Thanks for contacting Cymbal Home & Garden. How may I help you today?"
    ],
    "weather": [
        "It's currently sunny in Las Vegas with a temperature of 85°F. The forecast for the next few days shows continued clear skies with temperatures ranging from 82-90°F.",
        "In Las Vegas today, we're seeing clear skies with temperatures around 87°F. The forecast for the upcoming days shows similar conditions with temperatures in the mid-80s.",
        "The weather in Las Vegas is currently hot and sunny, with temperatures at 86°F. The forecast shows continuing warm weather with no precipitation expected in the next several days."
    ],
    "plants": [
        "For a dry climate like Las Vegas, I recommend drought-resistant plants such as agave, yucca, and various cacti. You might also consider desert marigolds or lantana for adding some color to your garden.",
        "In Las Vegas's climate, consider planting drought-tolerant options like lavender, sage, and rosemary. These not only survive well but also provide beautiful colors and scents.",
        "For your Las Vegas garden, I'd recommend succulents, desert willows, and red yucca. These plants are adapted to the hot, dry conditions and require minimal watering once established."
    ],
    "booking": [
        "I'd be happy to help you with booking a service. We have openings for garden consultations this weekend on Saturday at 10am and 2pm, and Sunday at 1pm. Would any of those times work for you?",
        "I can schedule a service appointment for you. We currently have availability for landscaping services on Saturday morning or Monday afternoon. What works best for your schedule?",
        "I can assist with booking a service. For garden planning consultations, we have available slots this Friday at 3pm, Saturday at 11am, and Monday at 9am. Would you like to schedule one of these times?"
    ],
    "firestore": [
        "I've checked your booking information in our database. You have a garden consultation scheduled for May 15th at 2:00 PM. Would you like to modify this booking?",
        "According to our records, you have 2 upcoming appointments: a garden consultation on May 15th and a planting service on June 3rd. Can I help you with either of these?",
        "I've saved your booking information to our database. Your confirmation number is GARDEN-2025-05-15. You can reference this number if you need to make any changes to your appointment."
    ],
    "default": [
        "Thank you for your message. As a customer service agent for Cymbal Home & Garden, I'm here to help with your gardening and home improvement needs. Is there something specific you'd like assistance with?",
        "I understand you're looking for assistance. As Cymbal Home & Garden's customer service agent, I can help with plant recommendations, gardening tips, and product information. What specifically are you interested in?",
        "Thanks for reaching out to Cymbal Home & Garden. I can provide information on our products, gardening advice for your climate, or help with scheduling services. What would be most helpful for you?"
    ]
}

def print_system_message(message):
    """Print a system message with formatting"""
    print(f"{Fore.YELLOW}System: {Style.RESET_ALL}{message}")

def print_agent_message(message):
    """Print a message from the agent with formatting"""
    print(f"{Fore.BLUE}Agent: {Style.RESET_ALL}{message}")

def print_user_message(message):
    """Print a user message with formatting"""
    print(f"{Fore.GREEN}You: {Style.RESET_ALL}{message}")

def get_response(message):
    """Generate a response based on the user's message"""
    message = message.lower()
    
    if any(word in message for word in ["hello", "hi", "hey", "howdy", "greetings"]):
        category = "greeting"
    elif any(word in message for word in ["weather", "forecast", "temperature", "climate", "rain", "sun", "hot", "cold"]):
        category = "weather"
    elif any(word in message for word in ["plant", "garden", "grow", "drought", "water", "flower", "tree", "shrub"]):
        category = "plants"
    elif any(word in message for word in ["book", "appointment", "schedule", "service", "consultation", "visit"]):
        category = "booking"
    elif any(word in message for word in ["database", "record", "stored", "information", "firestore", "data"]):
        category = "firestore"
    else:
        category = "default"
    
    # Use the first response in each category
    return RESPONSES[category][0]

def create_session():
    """Create a mock session"""
    session_id = str(uuid.uuid4())
    print_system_message(f"Created new session with ID: {session_id}")
    return session_id

def run_interactive_chat():
    """Run an interactive chat session with the agent"""
    print_system_message("Starting demo chat with Cymbal Home & Garden Customer Service Agent")
    print_system_message("This is a SIMULATION for testing the interface.")
    print_system_message("The actual web app would connect to the deployed agent in Vertex AI.")
    
    session_id = create_session()
    
    # Display welcome message
    print_agent_message("Welcome to Cymbal Home & Garden! I'm your customer service assistant. How can I help you today?")
    
    while True:
        # Get user input
        user_message = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        
        # Check for exit command
        if user_message.lower() in ["exit", "quit", "bye"]:
            print_agent_message("Thank you for chatting with Cymbal Home & Garden. Have a great day!")
            break
        
        # Simulate processing time
        print_system_message("Agent is thinking...")
        time.sleep(1)
        
        # Get and display response
        response = get_response(user_message)
        print_agent_message(response)

if __name__ == "__main__":
    run_interactive_chat()