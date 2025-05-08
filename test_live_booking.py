#!/usr/bin/env python3
"""
Script to test interaction with real booking in Firestore via the truck sharing agent.
"""

import sys
import os
import asyncio
import json

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from customer_service.tools.tools import interact_with_firestore

async def test_real_booking_interaction():
    """Test interaction with a real booking."""
    
    print("="*80)
    print("Testing Truck Sharing Agent with Real Booking Data")
    print("="*80)
    
    # 1. Query all bookings to find our sample booking
    query_params = {
        "filters": [
            {"field": "status", "op": "==", "value": "confirmed"}
        ]
    }
    
    # Convert query parameters to JSON string
    query_params_json = json.dumps(query_params)
    
    booking_query_result = await interact_with_firestore(f"query:bookings:{query_params_json}")
    print(f"\n1. Querying confirmed bookings:")
    print(booking_query_result)
    
    # Extract the booking ID from the result
    try:
        booking_data = json.loads(booking_query_result)
        if booking_data.get("success") and booking_data.get("documents"):
            booking_id = booking_data["documents"][0]["id"]
            print(f"\nFound booking ID: {booking_id}")
            
            # 2. Get the specific booking details
            booking_details = await interact_with_firestore(f"read:bookings:{booking_id}")
            print(f"\n2. Getting specific booking details:")
            print(booking_details)
            
            # 3. Update the booking status
            update_data = {"status": "in_progress"}
            update_data_json = json.dumps(update_data)
            update_result = await interact_with_firestore(f"update:bookings:{booking_id}:{update_data_json}")
            print(f"\n3. Updating booking status to 'in_progress':")
            print(update_result)
            
            # 4. Get the updated booking
            updated_booking = await interact_with_firestore(f"read:bookings:{booking_id}")
            print(f"\n4. Getting updated booking details:")
            print(updated_booking)
            
            # 5. Restore the original status
            restore_data = {"status": "confirmed"}
            restore_data_json = json.dumps(restore_data)
            restore_result = await interact_with_firestore(f"update:bookings:{booking_id}:{restore_data_json}")
            print(f"\n5. Restoring booking status to 'confirmed':")
            print(restore_result)
        else:
            print("No bookings found with status 'confirmed'")
    except Exception as e:
        print(f"Error processing booking data: {e}")
    
    print("\nTesting completed!")

if __name__ == "__main__":
    asyncio.run(test_real_booking_interaction())