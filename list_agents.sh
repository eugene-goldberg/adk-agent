#!/bin/bash

# Script to list ADK agents deployed on Vertex AI

# Set default project and region
PROJECT=${GOOGLE_CLOUD_PROJECT:-"simple-agent-project"}
REGION=${GOOGLE_CLOUD_LOCATION:-"us-central1"}

# Show usage information
function show_usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -p, --project PROJECT_ID  Specify the Google Cloud project ID"
  echo "  -r, --region REGION       Specify the region (default: us-central1)"
  echo "  -i, --id AGENT_ID         Get details for a specific agent ID"
  echo "  -h, --help                Show this help message"
  echo ""
  echo "Example:"
  echo "  $0 --project my-project --region us-central1"
  echo "  $0 --id 516304272124542976"
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
    -i|--id)
      AGENT_ID="$2"
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

# Get authentication token
TOKEN=$(gcloud auth print-access-token)

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed. Please install it with 'brew install jq'."
  exit 1
fi

# If an agent ID is provided, get details for that specific agent
if [ ! -z "$AGENT_ID" ]; then
  echo "Getting details for agent: $AGENT_ID..."
  curl -s -X GET \
    -H "Authorization: Bearer $TOKEN" \
    "https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT/locations/$REGION/reasoningEngines/$AGENT_ID" | \
    jq '.'
else
  # Otherwise, list all agents
  echo "Listing ADK agents in project: $PROJECT, region: $REGION..."
  curl -s -X GET \
    -H "Authorization: Bearer $TOKEN" \
    "https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT/locations/$REGION/reasoningEngines" | \
    jq -r '.reasoningEngines[] | "ID: " + (.name | split("/") | last) + 
           "\nCreated: " + .createTime + 
           "\nUpdated: " + .updateTime +
           "\nPython: " + .spec.packageSpec.pythonVersion + 
           "\nDisplay Name: " + (.displayName // "Not set") + 
           "\nDescription: " + (.description // "Not set") + 
           "\nStorage: " + .spec.packageSpec.pickleObjectGcsUri + "\n"'
fi