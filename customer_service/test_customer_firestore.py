#!/usr/bin/env python3
"""
Test script to demonstrate the integration of Firestore with the Customer Service agent.
This script runs a test conversation where the customer service agent uses the Firestore database
to retrieve and manage customer data and bookings.
"""

import os
import sys
import logging
import argparse
import vertexai
from dotenv import load_dotenv
from vertexai.preview import reasoning_engines

from customer_service.agent import root_agent
from customer_service.config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the Firestore integration with Customer Service Agent")
    parser.add_argument("--create_session", action="store_true", help="Create a new session")
    parser.add_argument("--run_test", action="store_true", help="Run the test conversation")
    parser.add_argument("--session_id", help="Session ID for testing")
    parser.add_argument("--user_id", default="test_user", help="User ID for session operations")
    return parser.parse_args()


def main():
    """Main function to run the Firestore integration test."""
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        sys.exit(1)
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        sys.exit(1)

    # Initialize Vertex AI
    logger.info(f"Initializing Vertex AI with project={project_id}, location={location}")
    vertexai.init(
        project=project_id,
        location=location,
    )

    # Create the app
    logger.info("Creating local app instance...")
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    if args.create_session:
        # Create a session
        logger.info(f"Creating session for user '{args.user_id}'...")
        session = app.create_session(user_id=args.user_id)
        logger.info(f"Session created: {session.id}")
        return

    if args.run_test:
        if not args.session_id:
            logger.error("Session ID is required for running the test.")
            logger.info("First create a session with: python customer_service/test_customer_firestore.py --create_session")
            sys.exit(1)
            
        # Example conversation showing Firestore integration
        queries = [
            "Hi, I'm looking for information about my recent bookings.",
            "Can you show me all the bookings in the system?",
            "I'd like to book a planting service for my petunias. Can you help me schedule that?",
            "Let's schedule it for May 15th between 9-12.",
            "Yes, please save that booking to the database.",
            "Can you show me my latest booking now?",
            "Thanks for your help!"
        ]
        
        # Run through the test conversation
        for query in queries:
            logger.info(f"Sending query: {query}")
            try:
                for event in app.stream_query(
                    user_id=args.user_id,
                    session_id=args.session_id,
                    message=query,
                ):
                    logger.info(f"Response event: {event}")
            except Exception as e:
                logger.error(f"Error during query: {e}")
                sys.exit(1)
                
        logger.info("Test completed successfully.")
        return
        
    # If no arguments are provided, show usage
    logger.info("Usage:")
    logger.info("  1. Create a session:")
    logger.info("     python customer_service/test_customer_firestore.py --create_session")
    logger.info("  2. Run the test conversation:")
    logger.info("     python customer_service/test_customer_firestore.py --run_test --session_id=YOUR_SESSION_ID")


if __name__ == "__main__":
    main()