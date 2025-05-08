#!/usr/bin/env python3
"""
Script to test Firestore integration with the truck sharing app's database schema.

This script tests the following operations against the truck app's Firestore collections:
1. Reading user profiles
2. Querying vehicles with filters
3. Creating a booking
4. Updating a booking status
5. Querying bookings by customer
6. Deleting a test booking

Requirements:
- A Google Cloud project with Firestore enabled
- Proper authentication (Application Default Credentials or service account)
- Firestore collections matching the truck app schema ('users', 'vehicles', 'bookings')
"""

import asyncio
import logging
import json
import uuid
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from customer_service.firestore_agent.agent import FirestoreAgent
from customer_service.tools.tools import interact_with_firestore

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_CUSTOMER_ID = "test_user_" + str(uuid.uuid4())[:8]
TEST_VEHICLE_ID = "test_vehicle_" + str(uuid.uuid4())[:8]
TEST_BOOKING_ID = "test_booking_" + str(uuid.uuid4())[:8]

# Generate pickup time 3 days from now
pickup_time = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")

async def test_truck_firestore_integration():
    """Test Firestore integration with truck app schema."""
    
    logger.info("Starting Firestore integration tests for truck app schema")
    
    # Initialize the agent directly
    firestore_agent = FirestoreAgent()
    
    # Check if the agent has initialized properly
    if firestore_agent.db is None:
        logger.error("Failed to initialize Firestore client. Check authentication and project settings.")
        return
    
    logger.info("Firestore client initialized successfully")
    
    try:
        # 1. Create a test user profile
        logger.info("\n\n1. Creating a test user profile")
        
        user_data = {
            "uid": TEST_CUSTOMER_ID,
            "name": "Test Customer",
            "email": "test.customer@example.com",
            "phone": "+1-555-123-4567",
            "role": "user",
            "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "hasCompletedOnboarding": True,
            "preferredNotifications": {
                "email": True,
                "sms": True,
                "push": True
            },
            "savedAddresses": {
                "home": "123 Test Home St, Test City, CA 12345",
                "work": "456 Test Work Ave, Test City, CA 12345"
            }
        }
        
        create_user_query = f"write:users:{TEST_CUSTOMER_ID}:{json.dumps(user_data)}"
        create_user_result = await firestore_agent.process_query(create_user_query)
        logger.info(f"Create user result: {create_user_result}")
        
        # 2. Create a test vehicle
        logger.info("\n\n2. Creating a test vehicle")
        
        vehicle_data = {
            "id": TEST_VEHICLE_ID,
            "ownerId": "test_owner_" + str(uuid.uuid4())[:8],
            "type": "pickup",
            "make": "Ford",
            "model": "F-150",
            "year": "2023",
            "licensePlate": "TEST123",
            "capacity": "Standard pickup bed",
            "hourlyRate": 45.00,
            "offerAssistance": True,
            "assistanceRate": 25.00,
            "isActive": True,
            "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "photos": {
                "front": "https://example.com/test_truck_front.jpg",
                "side": "https://example.com/test_truck_side.jpg"
            }
        }
        
        create_vehicle_query = f"write:vehicles:{TEST_VEHICLE_ID}:{json.dumps(vehicle_data)}"
        create_vehicle_result = await firestore_agent.process_query(create_vehicle_query)
        logger.info(f"Create vehicle result: {create_vehicle_result}")
        
        # 3. Read user profile using the interact_with_firestore tool
        logger.info("\n\n3. Reading user profile using the interact_with_firestore tool")
        
        user_read_result = await interact_with_firestore(f"read:users:{TEST_CUSTOMER_ID}")
        logger.info(f"User profile read result: {user_read_result}")
        
        # 4. Query vehicles with filters
        logger.info("\n\n4. Querying vehicles with filter for pickup trucks")
        
        query_params = {
            "filters": [
                {"field": "type", "op": "==", "value": "pickup"}
            ],
            "limit": 5
        }
        
        vehicle_query_result = await interact_with_firestore(f"query:vehicles:{json.dumps(query_params)}")
        logger.info(f"Vehicle query result: {vehicle_query_result}")
        
        # 5. Create a test booking
        logger.info("\n\n5. Creating a test booking")
        
        booking_data = {
            "id": TEST_BOOKING_ID,
            "customerId": TEST_CUSTOMER_ID,
            "vehicleId": TEST_VEHICLE_ID,
            "ownerId": vehicle_data["ownerId"],
            "pickupAddress": "123 Test Pickup St, Test City, CA 12345",
            "destinationAddress": "789 Test Destination Ave, Test City, CA 12345",
            "pickupDateTime": pickup_time,
            "estimatedHours": 3,
            "needsAssistance": True,
            "ridingAlong": True,
            "status": "pending",
            "totalCost": 210.00,
            "assistanceCost": 75.00,
            "cargoDescription": "Test furniture and boxes",
            "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        create_booking_query = f"write:bookings:{TEST_BOOKING_ID}:{json.dumps(booking_data)}"
        create_booking_result = await interact_with_firestore(create_booking_query)
        logger.info(f"Create booking result: {create_booking_result}")
        
        # 6. Update booking status
        logger.info("\n\n6. Updating booking status to confirmed")
        
        update_booking_query = f"update:bookings:{TEST_BOOKING_ID}:{json.dumps({'status': 'confirmed'})}"
        update_booking_result = await interact_with_firestore(update_booking_query)
        logger.info(f"Update booking result: {update_booking_result}")
        
        # 7. Query bookings by customer
        logger.info("\n\n7. Querying bookings for the test customer")
        
        bookings_query_params = {
            "filters": [
                {"field": "customerId", "op": "==", "value": TEST_CUSTOMER_ID}
            ]
        }
        
        bookings_query_result = await interact_with_firestore(f"query:bookings:{json.dumps(bookings_query_params)}")
        logger.info(f"Customer bookings query result: {bookings_query_result}")
        
        # 8. Clean up - delete the test booking
        logger.info("\n\n8. Cleaning up - deleting test booking")
        
        delete_booking_result = await interact_with_firestore(f"delete:bookings:{TEST_BOOKING_ID}")
        logger.info(f"Delete booking result: {delete_booking_result}")
        
        # 9. Clean up - delete test vehicle
        logger.info("\n\n9. Cleaning up - deleting test vehicle")
        
        delete_vehicle_result = await interact_with_firestore(f"delete:vehicles:{TEST_VEHICLE_ID}")
        logger.info(f"Delete vehicle result: {delete_vehicle_result}")
        
        # 10. Clean up - delete test user
        logger.info("\n\n10. Cleaning up - deleting test user")
        
        delete_user_result = await interact_with_firestore(f"delete:users:{TEST_CUSTOMER_ID}")
        logger.info(f"Delete user result: {delete_user_result}")
        
        logger.info("\n\nFirestore integration test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during Firestore integration test: {e}")
        
if __name__ == "__main__":
    logger.info("Starting truck app Firestore integration test")
    asyncio.run(test_truck_firestore_integration())