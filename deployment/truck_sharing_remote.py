"""
Remote deployment script for the Truck Sharing Agent.
"""

import os
import sys
import subprocess

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

from customer_service.agent import root_agent

# Check Python version first
python_version = sys.version_info
print(f"Current Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major == 3 and python_version.minor > 12:
    print("Warning: Vertex AI Agent Engine only supports Python up to 3.12.")
    print("Trying to run deployment with a compatible Python version...")
    
    # Try to find Python 3.12
    try:
        subprocess.run(["python3.12", "--version"], check=True)
        print("Found Python 3.12, will use it for deployment")
        subprocess.run(["python3.12"] + sys.argv)
        sys.exit(0)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Python 3.12 not found, continuing with current version...")

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP bucket.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")
flags.DEFINE_string("user_id", "test_user", "User ID for session operations.")
flags.DEFINE_string("session_id", None, "Session ID for operations.")
flags.DEFINE_bool("create", False, "Creates a new deployment.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployment.")
flags.DEFINE_bool("list", False, "Lists all deployments.")
flags.DEFINE_bool("create_session", False, "Creates a new session.")
flags.DEFINE_bool("list_sessions", False, "Lists all sessions for a user.")
flags.DEFINE_bool("get_session", False, "Gets a specific session.")
flags.DEFINE_bool("send", False, "Sends a message to the deployed agent.")
flags.DEFINE_string(
    "message",
    "Hi, I need a truck to move some furniture this weekend.",
    "Message to send to the agent.",
)
flags.mark_bool_flags_as_mutual_exclusive(
    [
        "create",
        "delete",
        "list",
        "create_session",
        "list_sessions",
        "get_session",
        "send",
    ]
)


def create() -> None:
    """Creates a new deployment."""
    # First wrap the agent in AdkApp
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Now deploy to Agent Engine using the latest SDK pattern
    try:
        print("Starting deployment, this may take several minutes...")
        print(f"Using Vertex AI SDK version: {vertexai.__version__ if hasattr(vertexai, '__version__') else 'unknown'}")
        
        # Use the latest SDK pattern
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
    except Exception as e:
        print(f"Deployment started but may still be in progress: {e}")
        print("Please check the Google Cloud Console or run --list to see if the deployment succeeded.")


def delete(resource_id: str) -> None:
    """Deletes an existing deployment."""
    remote_app = agent_engines.get(resource_id)
    remote_app.delete(force=True)
    print(f"Deleted remote app: {resource_id}")


def list_deployments() -> None:
    """Lists all deployments."""
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return
    print("Deployments:")
    for deployment in deployments:
        print(f"- {deployment.resource_name}")


def create_session(resource_id: str, user_id: str) -> None:
    """Creates a new session for the specified user."""
    remote_app = agent_engines.get(resource_id)
    remote_session = remote_app.create_session(user_id=user_id)
    print("Created session:")
    print(f"  Session ID: {remote_session['id']}")
    print(f"  User ID: {remote_session['user_id']}")
    print(f"  App name: {remote_session['app_name']}")
    print(f"  Last update time: {remote_session['last_update_time']}")
    print("\nUse this session ID with --session_id when sending messages.")


def list_sessions(resource_id: str, user_id: str) -> None:
    """Lists all sessions for the specified user."""
    remote_app = agent_engines.get(resource_id)
    sessions = remote_app.list_sessions(user_id=user_id)
    print(f"Sessions for user '{user_id}':")
    for session in sessions:
        print(f"- Session ID: {session['id']}")


def get_session(resource_id: str, user_id: str, session_id: str) -> None:
    """Gets a specific session."""
    remote_app = agent_engines.get(resource_id)
    session = remote_app.get_session(user_id=user_id, session_id=session_id)
    print("Session details:")
    print(f"  ID: {session['id']}")
    print(f"  User ID: {session['user_id']}")
    print(f"  App name: {session['app_name']}")
    print(f"  Last update time: {session['last_update_time']}")


def send_message(resource_id: str, user_id: str, session_id: str, message: str) -> None:
    """Sends a message to the deployed agent."""
    print(f"Sending message to session {session_id}:")
    print(f"Message: {message}")
    print("\nResponse:")
    
    # Print SDK versions for debugging
    import vertexai
    print(f"Vertex AI SDK version: {vertexai.__version__ if hasattr(vertexai, '__version__') else 'unknown'}")
    print(f"Python version: {sys.version}")
    
    try:
        # Get the remote app using the updated SDK
        print("Getting remote app...")
        remote_app = agent_engines.get(resource_id)
        
        # Standard API approach - try stream_query first as the preferred method
        print("Using stream_query method...")
        for event in remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            print(event)
        return
            
    except AttributeError as attr_err:
        print(f"stream_query not available: {attr_err}")
        # Fall back to REST API approach if stream_query is not available
        print("Falling back to REST API approach...")
        
        import requests
        import json
        import google.auth
        import google.auth.transport.requests
        
        # Get credentials and project ID
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
        
        # Construct the API endpoint for reasoning engines
        # Note: The resource_id might already contain the full path
        if resource_id.startswith("projects/"):
            # Use the resource_id as is if it's a full path
            base_path = resource_id
            numeric_id = resource_id.split('/')[-1]
        else:
            # Construct the full path if just the numeric ID is provided
            numeric_id = resource_id
            base_path = f"projects/{project_id}/locations/{location}/reasoningEngines/{numeric_id}"
            
        endpoint = f"https://{location}-aiplatform.googleapis.com/v1/{base_path}:streamQuery"
        print(f"Using API endpoint: {endpoint}")
        
        # Prepare the request payload
        payload = {
            "class_method": "stream_query",
            "input": {
                "user_id": user_id,
                "session_id": session_id,
                "message": message
            }
        }
        
        # Set headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Send the request
        print("Sending API request...")
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("API call successful!")
            
            # Process streaming response
            try:
                # The response can be a series of JSON objects separated by newlines
                lines = response.text.strip().split('\n')
                
                # Get the last response (most complete)
                last_response = None
                for line in lines:
                    if line.strip():
                        try:
                            parsed = json.loads(line.strip())
                            last_response = parsed
                        except json.JSONDecodeError:
                            continue
                
                if last_response:
                    print(f"API Response: {json.dumps(last_response, indent=2)}")
                    
                    # Extract the text from the response based on the expected structure
                    text_response = "No text found in response"
                    
                    # Check for content.parts[].text structure
                    if "content" in last_response and "parts" in last_response["content"]:
                        for part in last_response["content"]["parts"]:
                            if "text" in part:
                                text_response = part["text"]
                                break
                    
                    print(f"Response: {text_response}")
                else:
                    print("No valid JSON response found in the API response")
            except Exception as parse_err:
                print(f"Error parsing response: {parse_err}")
                print(f"Raw response: {response.text[:1000]}...")
        else:
            print(f"API call failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
            raise Exception(f"API call failed: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"Error sending message: {e}")
        print("\nDiagnostic information:")
        print(f"- Resource ID: {resource_id}")
        print(f"- Session ID: {session_id}")
        print(f"- User ID: {user_id}")
        
        # Re-raise the exception to ensure proper error handling
        raise


def main(argv=None):
    """Main function that can be called directly or through app.run()."""
    # Parse flags first
    if argv is None:
        argv = flags.FLAGS(sys.argv)
    else:
        argv = flags.FLAGS(argv)

    load_dotenv()

    # Now we can safely access the flags
    # Always use the pickuptruckapp project for Firestore integration
    project_id = FLAGS.project_id if FLAGS.project_id else "pickuptruckapp"
    location = FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = FLAGS.bucket if FLAGS.bucket else os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://pickuptruckapp-bucket")
    user_id = FLAGS.user_id
    
    print(f"Using project ID: {project_id}")
    print(f"Using location: {location}")
    print(f"Using bucket: {bucket}")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("Missing required environment variable: GOOGLE_CLOUD_STAGING_BUCKET")
        return

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    if FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("resource_id is required for delete")
            return
        delete(FLAGS.resource_id)
    elif FLAGS.list:
        list_deployments()
    elif FLAGS.create_session:
        if not FLAGS.resource_id:
            print("resource_id is required for create_session")
            return
        create_session(FLAGS.resource_id, user_id)
    elif FLAGS.list_sessions:
        if not FLAGS.resource_id:
            print("resource_id is required for list_sessions")
            return
        list_sessions(FLAGS.resource_id, user_id)
    elif FLAGS.get_session:
        if not FLAGS.resource_id:
            print("resource_id is required for get_session")
            return
        if not FLAGS.session_id:
            print("session_id is required for get_session")
            return
        get_session(FLAGS.resource_id, user_id, FLAGS.session_id)
    elif FLAGS.send:
        if not FLAGS.resource_id:
            print("resource_id is required for send")
            return
        if not FLAGS.session_id:
            print("session_id is required for send")
            return
        send_message(FLAGS.resource_id, user_id, FLAGS.session_id, FLAGS.message)
    else:
        print(
            "Please specify one of: --create, --delete, --list, --create_session, --list_sessions, --get_session, or --send"
        )


if __name__ == "__main__":
    app.run(main)