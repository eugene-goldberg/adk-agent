#!/bin/bash
# This script automates the discovery, connection, and testing of a deployed customer service agent on Vertex AI

# Set text colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set constants
PROJECT_ID="pickuptruckapp"
RESOURCE_ID="projects/843958766652/locations/us-central1/reasoningEngines/1818126039411326976"

# Print section headers with color
section() {
  echo -e "\n${YELLOW}========== $1 ==========${NC}\n"
}

# Run a command with proper environment variables
run_cmd() {
  echo -e "${BLUE}$ $1${NC}"
  eval $1
  if [ $? -ne 0 ]; then
    echo -e "${RED}Command failed${NC}"
  fi
  echo ""
}

# Make the script executable
chmod +x "$0"

# Start the process
section "DISCOVERING DEPLOYED AGENTS"
run_cmd "./list_agents.sh --project $PROJECT_ID"
echo -e "${GREEN}Agent ID: 1818126039411326976${NC}"

# Session creation instructions
section "CREATING A SESSION WITH THE AGENT"
echo -e "${YELLOW}To create a session, run the following command manually:${NC}"
echo -e "${BLUE}cd $(pwd) && export PYTHONPATH=$PYTHONPATH:$(pwd) && python deployment/customer_service_remote.py --create_session --resource_id=$RESOURCE_ID${NC}"
echo ""
echo -e "${YELLOW}Once you have created a session, you can test the agent using:${NC}"
echo -e "${BLUE}cd $(pwd) && export PYTHONPATH=$PYTHONPATH:$(pwd) && python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=YOUR_SESSION_ID --message=\"Your message here\"${NC}"
echo ""

# Suggested test messages
section "SUGGESTED TEST MESSAGES"
echo -e "${YELLOW}Here are some suggested test messages to use with the agent:${NC}"
echo ""
echo -e "1. ${GREEN}Basic interaction:${NC}"
echo -e "   ${BLUE}\"Hello, I'm looking for recommendations for plants that would do well in a desert climate.\"${NC}"
echo ""
echo -e "2. ${GREEN}Weather integration:${NC}"
echo -e "   ${BLUE}\"I'm interested in both flowers and cacti. What's the weather going to be like in Las Vegas this week, and which plants would be suitable based on the forecast?\"${NC}"
echo ""
echo -e "3. ${GREEN}Cart management:${NC}"
echo -e "   ${BLUE}\"Yes, please replace the standard potting soil with cactus mix and add the bloom-boosting fertilizer. Also, can you create a booking for a planting consultation next Friday at 2pm?\"${NC}"
echo ""
echo -e "4. ${GREEN}Booking creation:${NC}"
echo -e "   ${BLUE}\"Yes, Friday May 17th at 2pm works for me.\"${NC}"
echo -e "   ${BLUE}\"Yes, the afternoon slot from 1-4 PM works perfect for me.\"${NC}"
echo ""
echo -e "5. ${GREEN}Firestore integration - storing booking:${NC}"
echo -e "   ${BLUE}\"Yes, please send me the care instructions. Also, could you store my appointment in the Firestore database?\"${NC}"
echo ""
echo -e "6. ${GREEN}Firestore integration - retrieving booking:${NC}"
echo -e "   ${BLUE}\"Could you show me all my bookings in the Firestore database?\"${NC}"
echo -e "   ${BLUE}\"Could you tell me more about my most recent booking?\"${NC}"
echo ""

# Sample session flow
section "SAMPLE TESTING SESSION"
echo -e "${YELLOW}Here's a complete sequence of commands to test all functionality:${NC}"
echo ""
echo -e "export PYTHONPATH=$PYTHONPATH:$(pwd)"
echo -e "cd $(pwd)"
echo -e ""
echo -e "# Create a session"
echo -e "python deployment/customer_service_remote.py --create_session --resource_id=$RESOURCE_ID"
echo -e ""
echo -e "# Save the session ID (replace with your actual session ID)"
echo -e "SESSION_ID=your_session_id_here"
echo -e ""
echo -e "# Test basic interaction"
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Hello, I'm looking for recommendations for plants that would do well in a desert climate.\""
echo -e ""
echo -e "# Test weather integration"
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"I'm interested in both flowers and cacti. What's the weather going to be like in Las Vegas this week, and which plants would be suitable based on the forecast?\""
echo -e ""
echo -e "# Test cart management"
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Yes, please replace the standard potting soil with cactus mix and add the bloom-boosting fertilizer. Also, can you create a booking for a planting consultation next Friday at 2pm?\""
echo -e ""
echo -e "# Test booking creation"
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Yes, Friday May 17th at 2pm works for me.\""
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Yes, the afternoon slot from 1-4 PM works perfect for me.\""
echo -e ""
echo -e "# Test Firestore integration - storing booking"
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Yes, please send me the care instructions. Also, could you store my appointment in the Firestore database?\""
echo -e ""
echo -e "# Test Firestore integration - retrieving booking"
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Could you show me all my bookings in the Firestore database?\""
echo -e "python deployment/customer_service_remote.py --send --resource_id=$RESOURCE_ID --session_id=\$SESSION_ID --message=\"Could you tell me more about my most recent booking?\""
echo -e ""

# Instructions for running a complete shell session for testing
section "INSTRUCTIONS FOR AUTOMATED TESTING"
echo -e "${YELLOW}To run all tests in one automated session, copy the commands above into a shell script, replace 'your_session_id_here' with an actual session ID, and run it.${NC}"
echo -e ""
echo -e "${GREEN}The Customer Service Agent should be tested for:${NC}"
echo -e "1. Basic interaction capability"
echo -e "2. Weather integration through the Weather Agent"
echo -e "3. Cart management functionality"
echo -e "4. Booking creation and management"
echo -e "5. Firestore integration for storing and retrieving data"
echo -e ""
echo -e "${YELLOW}Happy testing!${NC}"