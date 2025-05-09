# Vertex AI Agent Redeployment Notes

## Summary of Changes

We updated and redeployed the Vertex AI agents with the latest SDK version (1.92.0) to address compatibility issues with the web API. This document outlines the changes made, current status, and next steps.

## Changes Made

1. **Updated Dependencies**
   - Updated `google-cloud-aiplatform` in requirements.txt from `>=1.33.0` to `[adk,agent_engines]==1.92.0`
   - Added explicit versions for all dependencies required by the Vertex AI SDK:
     - google-adk>=0.2.0
     - fastapi>=0.115.0
     - pydantic>=2.0.0
     - pydantic-settings==2.8.1
     - python-dotenv>=1.0.0
     - google-cloud-firestore>=2.16.1
     - requests>=2.31.0

2. **Updated Deployment Scripts**
   - Modified `customer_service_remote.py` and `truck_sharing_remote.py` to use the latest SDK patterns
   - Added better error handling and fallback mechanisms for API communication
   - Added diagnostic information to help debug issues

3. **Deleted Previous Deployments**
   - Removed three existing deployments:
     - `projects/843958766652/locations/us-central1/reasoningEngines/5570750428917792768` (truck-sharing-agent)
     - `projects/843958766652/locations/us-central1/reasoningEngines/9202903528392097792` (truck-sharing-agent)
     - `projects/843958766652/locations/us-central1/reasoningEngines/1818126039411326976` (customer-service-agent)

4. **Redeployed Agents**
   - Successfully redeployed the truck-sharing-agent: `projects/843958766652/locations/us-central1/reasoningEngines/1369314189046185984`
   - Successfully redeployed the customer-service-agent: `projects/843958766652/locations/us-central1/reasoningEngines/2753748861997547520`
   - Created an additional customer-service-agent deployment: `projects/843958766652/locations/us-central1/reasoningEngines/4957134979688562688`

## Current Status

Despite successful redeployment, we're still experiencing issues with agent communication:

1. **Session Creation**: We can successfully create sessions for all deployed agents.

2. **Message Communication**: We're unable to communicate with the deployed agents due to API compatibility issues:
   - The `stream_query` method is not available on the `AgentEngine` objects
   - The REST API endpoints return 404 errors
   - We have tried multiple approaches including direct SDK calls and REST API calls

3. **SDK Version Analysis**:
   - Previously using Vertex AI SDK version 1.89.0
   - Updated to version 1.92.0
   - The API patterns seem to have changed between these versions

## Technical Issues

1. **API Format Changes**:
   - The expected endpoint format has changed from previous versions
   - Attempts to use both `:query` and `:streamQuery` endpoints have failed
   - The error messages suggest that while we can create and list sessions, we cannot send messages to them

2. **SDK Method Availability**:
   - The redeployed agents don't expose the expected `stream_query` method
   - Error message from API: `User-specified method 'query'/'stream_query' not found. Available methods are: ['delete_session', 'list_sessions', 'create_session', 'get_session']`

## Next Steps

1. **Investigate Google Cloud Console**: Check the deployment logs in the Google Cloud Console for additional information: https://console.cloud.google.com/logs/query?project=pickuptruckapp

2. **Try ADK Direct Approach**: Consider using the ADK directly instead of the agent_engines approach:
   ```python
   from google.adk.sessions import VertexAiSessionService
   session_service = VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
   ```

3. **Check Google SDK Documentation**: Review the latest documentation for any API changes or deprecated methods: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/use/adk

4. **Explore API Versions**: Test using different API versions (v1, v1beta1) to see if that resolves the communication issues

5. **Consider Version Rollback**: If all else fails, consider rolling back to SDK version 1.89.0 if that's known to work with the existing code

## References

- Vertex AI SDK Documentation: https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk
- ADK Documentation: https://google.github.io/adk-docs/deploy/agent-engine/
- Vertex AI Agent Engine: https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview