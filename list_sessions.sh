#!/bin/bash

# Script to list sessions for an ADK agent deployed on Vertex AI

# Set default project and region
PROJECT=${GOOGLE_CLOUD_PROJECT:-"simple-agent-project"}
REGION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}
USER_ID="test_user"

# Show usage information
function show_usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -p, --project PROJECT_ID  Specify the Google Cloud project ID"
  echo "  -r, --region REGION       Specify the region (default: us-central1)"
  echo "  -a, --agent AGENT_ID      Required: Specify the agent ID"
  echo "  -u, --user USER_ID        Specify the user ID (default: test_user)"
  echo "  -s, --session SESSION_ID  Get details for a specific session ID"
  echo "  -h, --help                Show this help message"
  echo ""
  echo "Example:"
  echo "  $0 --agent 516304272124542976"
  echo "  $0 --agent 516304272124542976 --user custom_user_id"
  echo "  $0 --agent 516304272124542976 --session 8874110519024287744"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -p|--project)
      PROJECT="$2"
      shift 2
      ;;
    -r|--region)
      REGION="$2"
      shift 2
      ;;
    -a|--agent)
      AGENT_ID="$2"
      shift 2
      ;;
    -u|--user)
      USER_ID="$2"
      shift 2
      ;;
    -s|--session)
      SESSION_ID="$2"
      shift 2
      ;;
    -h|--help)
      show_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      show_usage
      exit 1
      ;;
  esac
done

# Check if agent ID is provided
if [ -z "$AGENT_ID" ]; then
  echo "Error: Agent ID is required"
  show_usage
  exit 1
fi

# Get authentication token
TOKEN=$(gcloud auth print-access-token)

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install it with 'brew install jq'."
  exit 1
fi

# Construct the agent resource name
AGENT_RESOURCE="projects/$PROJECT/locations/$REGION/reasoningEngines/$AGENT_ID"

# Get or list sessions
if [ ! -z "$SESSION_ID" ]; then
  # Get specific session
  echo "Getting details for session: $SESSION_ID..."
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "https://$REGION-aiplatform.googleapis.com/v1/$AGENT_RESOURCE:getSession" \
    -d "{\"user_id\":\"$USER_ID\",\"session_id\":\"$SESSION_ID\"}" | jq '.'
else
  # List all sessions for user
  echo "Listing sessions for user: $USER_ID..."
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "https://$REGION-aiplatform.googleapis.com/v1/$AGENT_RESOURCE:listSessions" \
    -d "{\"user_id\":\"$USER_ID\"}" | jq '.'
fi