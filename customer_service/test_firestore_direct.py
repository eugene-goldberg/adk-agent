#!/usr/bin/env python3
"""
Direct test script for Firestore integration with the Customer Service agent.
This script directly tests the interact_with_firestore function without using ADK sessions.
"""

import asyncio
import logging
import json
from customer_service.tools.tools import interact_with_firestore
from customer_service.firestore_agent.agent import FirestoreAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_firestore_direct():
    """Test the Firestore integration directly without ADK session management."""
    
    try:
        # Test different Firestore operations
        logger.info("1. Testing listing all bookings from the 'bookings' collection")
        query = "query:bookings:{}"
        result = await interact_with_firestore(query)
        logger.info(f"Result: {result}")
        
        # Parse the result for better display
        try:
            result_json = json.loads(result)
            if result_json.get("success") and "documents" in result_json:
                documents = result_json.get("documents", [])
                logger.info(f"Found {len(documents)} bookings")
                
                # Display booking details
                for i, doc in enumerate(documents, 1):
                    logger.info(f"Booking {i}:")
                    logger.info(f"  ID: {doc.get('id')}")
                    logger.info(f"  Status: {doc.get('status')}")
                    if 'formatted_pickup' in doc:
                        logger.info(f"  Pickup Time: {doc.get('formatted_pickup')}")
                    logger.info(f"  Customer ID: {doc.get('customerId')}")
        except json.JSONDecodeError:
            logger.error("Failed to parse result JSON")
        
        # Create a test booking
        logger.info("\n2. Creating a test booking")
        booking_id = f"test_booking_{int(asyncio.get_event_loop().time())}"
        booking_data = {
            "customerId": "123",
            "date": "2025-05-20",
            "time": "9-12",
            "status": "pending",
            "service": "planting",
            "details": "Planting petunias in the front garden"
        }
        create_query = f"write:bookings:{booking_id}:{json.dumps(booking_data)}"
        create_result = await interact_with_firestore(create_query)
        logger.info(f"Create result: {create_result}")
        
        # Read the booking we just created
        logger.info("\n3. Reading the test booking")
        read_query = f"read:bookings:{booking_id}"
        read_result = await interact_with_firestore(read_query)
        logger.info(f"Read result: {read_result}")
        
        # Update the booking
        logger.info("\n4. Updating the test booking")
        update_data = {
            "status": "confirmed",
            "notes": "Customer confirmed appointment"
        }
        update_query = f"update:bookings:{booking_id}:{json.dumps(update_data)}"
        update_result = await interact_with_firestore(update_query)
        logger.info(f"Update result: {update_result}")
        
        # Read the updated booking
        logger.info("\n5. Reading the updated booking")
        read_updated_result = await interact_with_firestore(read_query)
        logger.info(f"Updated booking: {read_updated_result}")
        
        # Query bookings with a filter - first try a complex query
        logger.info("\n6. Querying bookings - first with complex query (which may need an index)")
        query_params = {
            "filters": [
                {"field": "status", "op": "==", "value": "confirmed"}
            ],
            "limit": 10,
            "order_by": "date", 
            "direction": "ASCENDING"
        }
        query_string = f"query:bookings:{json.dumps(query_params)}"
        query_result = await interact_with_firestore(query_string)
        logger.info(f"Complex query result: {query_result}")
        
        # Now try a simpler query without sorting
        logger.info("\n6b. Querying bookings with a simpler query (no sorting)")
        simpler_params = {
            "filters": [
                {"field": "status", "op": "==", "value": "confirmed"}
            ],
            "limit": 10
        }
        simpler_query = f"query:bookings:{json.dumps(simpler_params)}"
        simpler_result = await interact_with_firestore(simpler_query)
        logger.info(f"Simple query result: {simpler_result}")
        
        # Delete the test booking
        logger.info("\n7. Deleting the test booking")
        delete_query = f"delete:bookings:{booking_id}"
        delete_result = await interact_with_firestore(delete_query)
        logger.info(f"Delete result: {delete_result}")
        
        # Confirm deletion
        logger.info("\n8. Confirming booking deletion")
        read_after_delete = await interact_with_firestore(read_query)
        logger.info(f"Read after delete: {read_after_delete}")
        
        logger.info("\nAll tests completed successfully!")
    
    except Exception as e:
        logger.error(f"Error during test: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_firestore_direct())