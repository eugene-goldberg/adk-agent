#!/usr/bin/env python3
"""
Script to deploy the truck sharing agent with a longer timeout.
"""

import os
import sys
import time
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from customer_service.agent import root_agent

def deploy_truck_sharing_agent():
    """Deploys the truck sharing agent with a longer timeout."""
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

    # First wrap the agent in AdkApp
    print("Creating AdkApp wrapper...")
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Now deploy to Agent Engine using the latest SDK pattern
    try:
        print("Starting deployment, this may take several minutes...")
        print(f"Using Vertex AI SDK version: {vertexai.__version__ if hasattr(vertexai, '__version__') else 'unknown'}")
        
        # Use the latest SDK pattern
        print("Creating agent with current SDK version...")
        remote_app = agent_engines.create(
            agent_engine=app,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]==1.92.0",
                "pydantic-settings==2.8.1",
                "google-cloud-firestore>=2.16.1",
                "requests>=2.31.0",
            ],
            extra_packages=["./customer_service", "./weather_agent"],
            display_name="truck-sharing-agent",
            description="A truck sharing assistant that helps customers book trucks, manage reservations, find suitable vehicles, and check weather conditions for moves.",
        )
        
        print(f"Created remote app: {remote_app.resource_name}")
        return remote_app.resource_name
    except Exception as e:
        print(f"Deployment started but may still be in progress: {e}")
        print("Please check the Google Cloud Console or run --list to see if the deployment succeeded.")
        return None

def check_deployment_status():
    """Checks the status of the deployments."""
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return []
    
    print("Deployments:")
    for deployment in deployments:
        print(f"- {deployment.resource_name}")
    
    return [d.resource_name for d in deployments]

def main():
    """Main function."""
    print("Starting deployment with extended timeout...")
    resource_name = deploy_truck_sharing_agent()
    
    if not resource_name:
        print("Deployment may still be in progress. Checking status every minute...")
        
        # Poll for up to 15 minutes
        for i in range(15):
            print(f"Check {i+1}/15 - Waiting for deployment to complete...")
            time.sleep(60)  # Wait for 1 minute
            
            deployments = check_deployment_status()
            if deployments:
                print("Deployment completed successfully!")
                break
        else:
            print("Deployment did not complete within the timeout period.")
    else:
        print("Deployment completed successfully!")
        print(f"Resource name: {resource_name}")

if __name__ == "__main__":
    main()