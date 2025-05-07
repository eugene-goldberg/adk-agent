#!/usr/bin/env python3
"""
Script to test actual Firestore connectivity and interaction.

This script tests all basic Firestore operations:
1. Writing a document to a collection
2. Reading a document from a collection
3. Updating an existing document
4. Querying documents with filters
5. Deleting a document
6. Listing all documents from a specific collection (bookings)

Requirements:
- A Google Cloud project with Firestore enabled
- Proper authentication (Application Default Credentials or service account)
- Firestore collection named "bookings" with at least one document
"""

import asyncio
import logging
import json
import uuid
from customer_service.firestore_agent.agent import FirestoreAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_firestore_operations():
    """Test basic Firestore operations with a live database."""
    
    # Initialize FirestoreAgent
    agent = FirestoreAgent()
    if agent.db is None:
        logger.error("Failed to initialize Firestore client. Check authentication and project settings.")
        return
    
    logger.info("Firestore client initialized successfully.")
    
    # Generate a unique test ID to avoid collisions
    test_id = str(uuid.uuid4())[:8]
    collection_name = f"test_collection_{test_id}"
    document_id = f"test_doc_{test_id}"
    
    try:
        # 1. Write a document
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "active": True,
            "score": 42,
            "tags": ["test", "sample"]
        }
        
        write_query = f"write:{collection_name}:{document_id}:{json.dumps(test_data)}"
        logger.info(f"1. Testing write operation: {write_query}")
        write_result = await agent.process_query(write_query)
        logger.info(f"Write result: {write_result}")
        
        # 2. Read the document
        read_query = f"read:{collection_name}:{document_id}"
        logger.info(f"2. Testing read operation: {read_query}")
        read_result = await agent.process_query(read_query)
        logger.info(f"Read result: {read_result}")
        
        # 3. Update the document
        update_data = {
            "active": False,
            "score": 85
        }
        update_query = f"update:{collection_name}:{document_id}:{json.dumps(update_data)}"
        logger.info(f"3. Testing update operation: {update_query}")
        update_result = await agent.process_query(update_query)
        logger.info(f"Update result: {update_result}")
        
        # 4. Read again to verify update
        logger.info(f"4. Reading updated document")
        read_updated_result = await agent.process_query(read_query)
        logger.info(f"Updated document: {read_updated_result}")
        
        # 5. Query the collection
        query_params = {
            "filters": [
                {"field": "active", "op": "==", "value": False}
            ],
            "limit": 10
        }
        # Use json.dumps with separators to avoid any whitespace issues
        query_string = f"query:{collection_name}:{json.dumps(query_params, separators=(',', ':'))}"
        logger.info(f"5. Testing query operation: {query_string}")
        query_result = await agent.process_query(query_string)
        logger.info(f"Query result: {query_result}")
        
        # 6. Delete the document
        delete_query = f"delete:{collection_name}:{document_id}"
        logger.info(f"6. Testing delete operation: {delete_query}")
        delete_result = await agent.process_query(delete_query)
        logger.info(f"Delete result: {delete_result}")
        
        # 7. Verify deletion
        logger.info(f"7. Verifying document is deleted")
        read_after_delete = await agent.process_query(read_query)
        logger.info(f"Read after delete: {read_after_delete}")
        
        # 8. List all documents from the bookings collection
        logger.info(f"8. Listing all documents from the bookings collection")
        # Using an empty JSON object as query parameters will retrieve all documents
        bookings_query = "query:bookings:{}"
        bookings_result = await agent.process_query(bookings_query)
        logger.info(f"Bookings collection results: {bookings_result}")
        
        # Parse and display the number of bookings found
        try:
            result_dict = json.loads(bookings_result)
            if result_dict.get("success"):
                documents = result_dict.get("documents", [])
                logger.info(f"Found {len(documents)} documents in the bookings collection")
                
                # Display some information about each booking
                for i, doc in enumerate(documents, 1):
                    logger.info(f"Booking {i}:")
                    logger.info(f"  ID: {doc.get('id')}")
                    logger.info(f"  Status: {doc.get('status')}")
                    logger.info(f"  Created At: {doc.get('createdAt')}")
        except json.JSONDecodeError:
            logger.error("Failed to parse bookings result")
        
        logger.info("Firestore operations test completed successfully.")
        
    except Exception as e:
        logger.error(f"Error during Firestore operations test: {e}")
    
if __name__ == "__main__":
    asyncio.run(test_firestore_operations())