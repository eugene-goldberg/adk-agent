#!/usr/bin/env python3
"""
Script to list the details of existing Vertex AI Agent Engine deployments.
"""

import os
import sys
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

def main():
    """Lists all deployments with details."""
    load_dotenv()

    print("Initializing Vertex AI...")
    # Always use the pickuptruckapp project for Firestore integration
    project_id = "pickuptruckapp"
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://pickuptruckapp-bucket")
    
    print(f"Using project ID: {project_id}")
    print(f"Using location: {location}")
    print(f"Using bucket: {bucket}")

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    print("\nListing deployments with details:")
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return
    
    print("DISPLAY NAME | RESOURCE NAME | CREATION TIME")
    print("-" * 80)
    for deployment in deployments:
        try:
            print(f"{deployment.display_name} | {deployment.resource_name}")
        except Exception as e:
            print(f"Error getting details for {deployment.resource_name}: {e}")
            # Try to print any available attributes
            for attr in dir(deployment):
                if not attr.startswith('_'):
                    try:
                        value = getattr(deployment, attr)
                        if not callable(value):
                            print(f"  {attr}: {value}")
                    except Exception:
                        pass

if __name__ == "__main__":
    main()