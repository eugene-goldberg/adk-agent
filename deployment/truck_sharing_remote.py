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

    # Now deploy to Agent Engine
    try:
        print("Starting deployment, this may take several minutes...")
        remote_app = agent_engines.create(
            agent_engine=app,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]",
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
    remote_app = agent_engines.get(resource_id)
    
    print(f"Sending message to session {session_id}:")
    print(f"Message: {message}")
    print("\nResponse:")
    
    # Due to API limitations, we need to use a CLI approach
    # We'll use the gcloud command line to send a message to the agent
    try:
        import subprocess
        import json
        import tempfile
        
        # Create a temporary file with the message content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp:
            request_json = {
                "query": message,
                "session_id": session_id,
                "user_id": user_id
            }
            json.dump(request_json, temp)
            temp_filename = temp.name
        
        # Construct the gcloud command
        cmd = [
            "gcloud", "alpha", "ai", "reasoning-engines", "run",
            f"--project={remote_app.project}",
            f"--location={remote_app.location}",
            f"--reasoning-engine={resource_id}",
            f"--session-id={session_id}",
            f"--request-file={temp_filename}"
        ]
        
        print("Executing command:", " ".join(cmd))
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print the output
        if result.returncode == 0:
            print("Command successful!")
            print("Output:")
            print(result.stdout)
        else:
            print("Command failed!")
            print("Error:")
            print(result.stderr)
            
        # Clean up the temporary file
        import os
        os.unlink(temp_filename)
    except Exception as e:
        print(f"Error sending message: {e}")
        
        # Print information about the agent
        print("\nAgent information:")
        print(f"- Resource name: {remote_app.resource_name}")
        print(f"- Display name: {remote_app.display_name}")
        print(f"- Methods: {[m for m in dir(remote_app) if not m.startswith('_') and callable(getattr(remote_app, m))]}")
        
        # Provide user with instructions for manual testing
        print("\nYou can test the agent manually with the following command:")
        print(f"gcloud alpha ai reasoning-engines run --project=pickuptruckapp --location=us-central1 --reasoning-engine={resource_id} --session-id={session_id} --query=\"{message}\"")
        
        print("\nOr visit the Google Cloud Console to test the agent:")
        print(f"https://console.cloud.google.com/vertex-ai/generative/reasoning-engines/details/{resource_id}?project=pickuptruckapp")


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