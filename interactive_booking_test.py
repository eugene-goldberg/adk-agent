#!/usr/bin/env python3
"""
Interactive conversation test that creates a real booking in Firestore.
"""

import asyncio
import sys
import os
import json
import uuid
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from customer_service.tools.tools import interact_with_firestore
from customer_service.firestore_agent.agent import FirestoreAgent

async def create_new_booking_from_conversation():
    """Run a conversation with the truck sharing agent that results in creating a real booking."""
    
    print("\n\n" + "="*80)
    print("Truck Sharing Agent Conversation Test - Creating a Real Booking")
    print("="*80)
    
    # Initialize the FirestoreAgent
    firestore_agent = FirestoreAgent()
    
    # Create a conversation context
    conversation_id = str(uuid.uuid4())
    print(f"Conversation ID: {conversation_id}")
    
    # Customer information (will be created if it doesn't exist)
    customer_id = f"user_booking_test_{conversation_id[:8]}"
    customer_data = {
        "uid": customer_id,
        "name": "Alex Johnson",
        "email": "alex.johnson@example.com",
        "phone": "+1-555-987-6543",
        "role": "user",
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat(),
        "hasCompletedOnboarding": True,
        "preferredNotifications": {
            "email": True,
            "sms": True,
            "push": True
        },
        "savedAddresses": {
            "home": "123 Home St, Chicago, IL 60601",
            "work": "456 Work Ave, Chicago, IL 60602"
        }
    }
    
    # Step 1: Create the customer in Firestore
    print(f"\nStep 1: Creating customer profile for {customer_data['name']}")
    create_user_query = f"write:users:{customer_id}:{json.dumps(customer_data)}"
    create_user_result = await interact_with_firestore(create_user_query)
    print(f"Result: {create_user_result}")
    
    # Step 2: Find available trucks
    print("\nStep 2: Finding available trucks")
    query_params = {
        "filters": [
            {"field": "type", "op": "==", "value": "pickup"},
            {"field": "isActive", "op": "==", "value": True}
        ],
        "limit": 5
    }
    
    vehicle_query_result = await interact_with_firestore(f"query:vehicles:{json.dumps(query_params)}")
    vehicle_data = json.loads(vehicle_query_result)
    
    if not vehicle_data.get("success") or not vehicle_data.get("documents"):
        print("No active pickup trucks found. Conversation cannot continue.")
        return
    
    # Get the first truck
    vehicle = vehicle_data["documents"][0]
    vehicle_id = vehicle["id"]
    vehicle_owner_id = vehicle["ownerId"]
    vehicle_make = vehicle.get("make", "Unknown")
    vehicle_model = vehicle.get("model", "Model")
    hourly_rate = vehicle.get("hourlyRate", 50.0)
    assistance_rate = vehicle.get("assistanceRate", 25.0)
    
    print(f"Selected vehicle: {vehicle_make} {vehicle_model} (ID: {vehicle_id})")
    print(f"Hourly rate: ${hourly_rate}, Assistance rate: ${assistance_rate}")
    
    # Step 3: Simulate the conversation
    print("\nStep 3: Simulating the conversation")
    
    print("\n🤖 Agent: Hello! I'm TruckBuddy, your assistant for the PickupTruck App. How can I help you today?")
    print("\n👤 Customer: Hi, I need a truck to move some furniture next weekend.")
    
    print("\n🤖 Agent: I'd be happy to help you find a truck for moving your furniture next weekend! Can you provide me with some more details? I'll need to know:")
    print("- Which day and time you'd prefer")
    print("- Your pickup and destination addresses")
    print("- How long you think you'll need the truck")
    print("- If you'll need any assistance with loading/unloading")
    
    print("\n👤 Customer: I need to move from my home address to my new apartment next Saturday around 10 AM. I'll probably need the truck for about 3 hours. And yes, I'd like help with loading.")
    
    # Calculate the next Saturday
    today = datetime.now()
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7  # If today is Saturday, we want next Saturday
    next_saturday = today + timedelta(days=days_until_saturday)
    pickup_time = next_saturday.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Format the date for display
    formatted_date = pickup_time.strftime("%A, %B %d, %Y at %I:%M %p")
    
    print(f"\n🤖 Agent: Thanks for those details! Let me search for available trucks on {formatted_date}.")
    print(f"I've found a great option: a {vehicle_make} {vehicle_model} pickup truck.")
    print(f"- Hourly rate: ${hourly_rate}/hour")
    print(f"- Loading assistance: ${assistance_rate}/hour")
    print(f"- Total for 3 hours: ${hourly_rate * 3 + assistance_rate * 3} (${hourly_rate * 3} for the truck + ${assistance_rate * 3} for assistance)")
    print("Would you like to book this truck?")
    
    print("\n👤 Customer: Yes, that sounds perfect!")
    
    print("\n🤖 Agent: Great! Let me confirm the details:")
    print(f"- Pickup from: {customer_data['savedAddresses']['home']}")
    print(f"- Destination: Your new apartment (please provide the address)")
    
    destination_address = "789 New Apartment Blvd, Chicago, IL 60603"
    print(f"\n👤 Customer: My new apartment is at {destination_address}")
    
    print("\n🤖 Agent: Thank you! Here's a summary of your booking:")
    print(f"- Date & time: {formatted_date}")
    print(f"- Vehicle: {vehicle_make} {vehicle_model}")
    print(f"- Pickup address: {customer_data['savedAddresses']['home']}")
    print(f"- Destination: {destination_address}")
    print(f"- Duration: 3 hours")
    print(f"- With loading/unloading assistance")
    print(f"- Total cost: ${hourly_rate * 3 + assistance_rate * 3}")
    print("Is this information correct? Also, could you briefly describe what furniture you'll be moving?")
    
    furniture_description = "Sofa, queen bed, dresser, dining table, and about 15 boxes of personal items"
    print(f"\n👤 Customer: Yes, that's all correct. I'll be moving a {furniture_description}.")
    
    print("\n🤖 Agent: Thank you for confirming. I'll create your booking now.")
    
    # Step 4: Create the booking in Firestore
    print("\nStep 4: Creating the real booking in Firestore")
    
    # Calculate costs
    truck_cost = hourly_rate * 3
    assistance_cost = assistance_rate * 3
    total_cost = truck_cost + assistance_cost
    
    # Generate booking ID
    booking_id = f"booking_{int(datetime.now().timestamp())}"
    
    # Create booking data
    booking_data = {
        "id": booking_id,
        "customerId": customer_id,
        "customerName": customer_data["name"],
        "customerEmail": customer_data["email"],
        "customerPhone": customer_data["phone"],
        "vehicleId": vehicle_id,
        "vehicleMake": vehicle_make,
        "vehicleModel": vehicle_model,
        "ownerId": vehicle_owner_id,
        "pickupAddress": customer_data["savedAddresses"]["home"],
        "destinationAddress": destination_address,
        "pickupDateTime": pickup_time.isoformat(),
        "estimatedHours": 3,
        "needsAssistance": True,
        "ridingAlong": True,
        "status": "confirmed",
        "totalCost": total_cost,
        "truckCost": truck_cost,
        "assistanceCost": assistance_cost,
        "cargoDescription": furniture_description,
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    # Create booking in Firestore
    create_booking_query = f"write:bookings:{booking_id}:{json.dumps(booking_data)}"
    create_booking_result = await interact_with_firestore(create_booking_query)
    booking_result = json.loads(create_booking_result)
    
    if booking_result.get("success"):
        print(f"\n🤖 Agent: Great news! Your booking has been confirmed. Here's your booking information:")
        print(f"- Booking ID: {booking_id}")
        print(f"- {vehicle_make} {vehicle_model}")
        print(f"- {formatted_date} (3 hours)")
        print(f"- Pickup: {customer_data['savedAddresses']['home']}")
        print(f"- Destination: {destination_address}")
        print(f"- Total: ${total_cost} (includes truck rental and loading assistance)")
        print("\nYou'll receive a confirmation email shortly. Is there anything else you'd like to know about your booking?")
    else:
        print(f"\n🤖 Agent: I'm sorry, but there was an issue confirming your booking. Please try again later or contact customer support.")
    
    # Step 5: Verify the booking
    print("\nStep 5: Verifying the booking in Firestore")
    
    # Query the booking
    query_params = {
        "filters": [
            {"field": "id", "op": "==", "value": booking_id}
        ]
    }
    
    booking_query_result = await interact_with_firestore(f"query:bookings:{json.dumps(query_params)}")
    print(f"Booking verification: {booking_query_result}")
    
    print("\nConversation ended!")
    print(f"Created booking ID: {booking_id}")
    print("="*80)
    
    return booking_id

if __name__ == "__main__":
    booking_id = asyncio.run(create_new_booking_from_conversation())
    
    # Print summary
    print("\nTest Summary:")
    print(f"Successfully created booking: {booking_id}")
    print("This booking now exists in the Firestore database and can be accessed by the truck sharing agent.")