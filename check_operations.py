#!/usr/bin/env python3
"""
Script to check the status of ongoing Vertex AI operations.
"""

import os
import vertexai
from dotenv import load_dotenv
from google.cloud import aiplatform

def main():
    """Check the status of ongoing operations."""
    load_dotenv()

    print("Initializing Vertex AI...")
    # Always use the pickuptruckapp project for Firestore integration
    project_id = "pickuptruckapp"
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    print(f"Using project ID: {project_id}")
    print(f"Using location: {location}")

    # Initialize the Vertex AI API client
    client = aiplatform.gapic.OperationServiceClient(
        client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
    )

    # Get the operations for this project and location
    request = aiplatform.gapic.ListOperationsRequest(
        name=f"projects/{project_id}/locations/{location}"
    )
    
    try:
        print("\nListing operations:")
        response = client.list_operations(request=request)
        
        if not response.operations:
            print("No operations found.")
            return
        
        print("OPERATION NAME | DONE | METADATA")
        print("-" * 80)
        for operation in response.operations:
            print(f"{operation.name} | {operation.done} | {operation.metadata}")
    except Exception as e:
        print(f"Error listing operations: {e}")

if __name__ == "__main__":
    main()