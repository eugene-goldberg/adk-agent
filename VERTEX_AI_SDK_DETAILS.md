# Vertex AI SDK and ADK Version Details

This document provides comprehensive information about the Vertex AI SDK and Agent Development Kit (ADK) versions used in this project, along with important compatibility notes and deployment requirements.

## Current Versions (May 2025)

### Core Requirements

- **Python Version**: 3.12.10
- **Vertex AI SDK Version**: 1.92.0
- **Google ADK Version**: 0.2.0

### Detailed Dependencies

```
google-cloud-aiplatform[adk,agent_engines]==1.92.0
google-adk>=0.2.0
pydantic>=2.0.0
pydantic-settings==2.8.1
google-cloud-firestore>=2.16.1
requests>=2.31.0
python-dotenv>=1.0.0
flask>=2.0.0
```

## Deployment IDs

Currently deployed agent instances:

- **Truck Sharing Agent**: `projects/843958766652/locations/us-central1/reasoningEngines/1369314189046185984`
- **Customer Service Agent**: `projects/843958766652/locations/us-central1/reasoningEngines/2753748861997547520`

## API Communication Details

### Endpoint Structure

For communicating with the deployed agents, the correct endpoint format is:

```
https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/reasoningEngines/{resource_id}:streamQuery
```

### API Payload Format

The proper payload format for the Vertex AI API (version 1.92.0):

```json
{
    "class_method": "stream_query",
    "input": {
        "user_id": "test_user",
        "session_id": "YOUR_SESSION_ID",
        "message": "Your message here"
    }
}
```

### Response Format

The response is typically a series of JSON objects, with the following structure for text-based responses:

```json
{
    "content": {
        "parts": [
            {
                "text": "The text response from the agent"
            }
        ]
    }
}
```

## Version Compatibility Notes

1. **Python Compatibility**:
   - Vertex AI Agent Engine requires Python ≥ 3.12
   - The code has been tested with Python 3.12.10

2. **SDK Version Evolution**:
   - Previously used Vertex AI SDK version 1.89.0
   - Updated to 1.92.0 in May 2025
   - API interfaces changed between these versions

3. **Client Library Compatibility**:
   - The `stream_query` method may not be directly available on `AgentEngine` objects
   - Direct REST API calls via the `:streamQuery` endpoint are more reliable

4. **ADK Compatibility**:
   - ADK version 0.2.0+ is required for proper deployment
   - Earlier versions may have incompatible model interfaces

## Deployment Requirements

When deploying agents to Vertex AI, include the following dependencies explicitly:

```python
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
    description="Agent description here"
)
```

## Common Issues and Solutions

1. **Python Version Mismatch**:
   - Error: `AttributeError: module 'google.cloud.aiplatform' has no attribute 'agent_engines'`
   - Solution: Ensure you're using Python 3.12+

2. **SDK Version Incompatibility**:
   - Error: `'AgentEngine' object has no attribute 'stream_query'`
   - Solution: Use direct REST API calls with the `:streamQuery` endpoint

3. **Missing Dependencies**:
   - Error: `ModuleNotFoundError: No module named 'pydantic_settings'`
   - Solution: Explicitly include all dependencies in the `requirements` list during deployment

4. **Authentication Issues**:
   - Error: `{'error': {'code': 401, 'message': 'Request had invalid authentication credentials.'}}`
   - Solution: Ensure proper Google Cloud authentication is set up with `gcloud auth application-default set-quota-project pickuptruckapp`

## Resources

- [Vertex AI SDK Documentation](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
- [Agent Development Kit (ADK) Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development/adk)
- [Reasoning Engines API Reference](https://cloud.google.com/vertex-ai/generative-ai/docs/reasoning-engines)
- [Python Client for Vertex AI](https://googleapis.dev/python/aiplatform/latest/index.html)