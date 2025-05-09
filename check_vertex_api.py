"""
Check Vertex AI API capabilities for agent engines.
"""

import os
import sys
import inspect
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_module_info(module):
    """Print information about a module."""
    print(f"\nModule: {module.__name__}")
    print(f"Version: {getattr(module, '__version__', 'Unknown')}")
    print(f"Path: {module.__file__}")
    
    # List classes and functions
    classes = []
    functions = []
    constants = []
    
    for name, obj in inspect.getmembers(module):
        if name.startswith('_'):
            continue
            
        if inspect.isclass(obj):
            classes.append(name)
        elif inspect.isfunction(obj):
            functions.append(name)
        elif not inspect.ismodule(obj):
            constants.append(name)
    
    print(f"\nClasses ({len(classes)}):")
    for cls in sorted(classes):
        print(f"  - {cls}")
    
    print(f"\nFunctions ({len(functions)}):")
    for func in sorted(functions):
        print(f"  - {func}")
    
    print(f"\nConstants/Variables ({len(constants)}):")
    for const in sorted(constants):
        print(f"  - {const}")

def check_agent_engine_methods():
    """Check methods available on AgentEngine objects."""
    print("\n=== Checking AgentEngine Methods ===")
    
    # Initialize Vertex AI
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://pickuptruckapp-bucket")
    
    print(f"Initializing Vertex AI with project={project_id}, location={location}")
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )
    
    # Get AgentEngine class and inspect it
    print("\nInspecting AgentEngine class:")
    agent_engine_class = agent_engines.AgentEngine
    methods = [name for name, _ in inspect.getmembers(agent_engine_class, predicate=inspect.isfunction)]
    for method in sorted(methods):
        if not method.startswith('_'):
            print(f"  - {method}")
    
    # Try direct API with google.cloud.aiplatform
    print("\nChecking google.cloud.aiplatform for agent capabilities:")
    try:
        from google.cloud import aiplatform
        
        # Check available clients
        clients = [name for name in dir(aiplatform.gapic) if "client" in name.lower()]
        print("\nAvailable API clients:")
        for client in sorted(clients):
            print(f"  - {client}")
            
        # Check for specific reasoning engine clients
        reasoning_clients = [name for name in clients if "reason" in name.lower()]
        if reasoning_clients:
            print("\nReasoning engine related clients:")
            for client in reasoning_clients:
                print(f"  - {client}")
                
        # Try to get the API discovery document
        print("\nTrying to access reasoning engines API:")
        try:
            from google.api_core.client_options import ClientOptions
            from google.cloud.aiplatform_v1 import ReasoningEngineServiceClient
            
            client_options = ClientOptions(
                api_endpoint=f"{location}-aiplatform.googleapis.com"
            )
            
            api_client = ReasoningEngineServiceClient(client_options=client_options)
            print(f"Successfully created ReasoningEngineServiceClient")
            
            # List available methods
            api_methods = [name for name in dir(api_client) if not name.startswith('_') and callable(getattr(api_client, name))]
            print("\nAvailable API methods:")
            for method in sorted(api_methods):
                print(f"  - {method}")
                
        except ImportError:
            print("ReasoningEngineServiceClient not available in this version")
        except Exception as api_err:
            print(f"Error accessing ReasoningEngineServiceClient: {api_err}")
    
    except Exception as e:
        print(f"Error accessing google.cloud.aiplatform: {e}")
        
    # Try listing deployments (with error handling)
    try:
        print("\nListing all deployments (handling encryption_spec error):")
        try:
            deployments = agent_engines.list()
        except Exception as list_err:
            if "encryption_spec" in str(list_err):
                print("Caught encryption_spec error. Trying workaround...")
                # This is a hack to patch the class to avoid the encryption_spec error
                import types
                original_to_dict = agent_engines.AgentEngine.to_dict
                
                def patched_to_dict(self):
                    result = {}
                    for key in self.__dict__:
                        if key == '_gca_resource' or key.startswith('_'):
                            continue
                        if key != 'encryption_spec':  # Skip the problematic field
                            result[key] = getattr(self, key)
                    return result
                
                agent_engines.AgentEngine.to_dict = types.MethodType(patched_to_dict, agent_engines.AgentEngine)
                deployments = agent_engines.list()
                # Restore original method
                agent_engines.AgentEngine.to_dict = original_to_dict
            else:
                raise
            
        if not deployments:
            print("No deployments found.")
            return
            
        for i, deployment in enumerate(deployments):
            print(f"\nDeployment #{i+1}:")
            print(f"  Resource name: {deployment.resource_name}")
            print(f"  Display name: {deployment.display_name}")
            
            # Check available methods (safely)
            print("\n  Available methods:")
            try:
                methods = [m for m in dir(deployment) if not m.startswith('_') and callable(getattr(deployment, m))]
                for method in sorted(methods):
                    print(f"    - {method}")
            except Exception as method_err:
                print(f"  Error listing methods: {method_err}")
    except Exception as e:
        print(f"Error listing deployments: {e}")

def main():
    """Main function."""
    # Print Vertex AI module info
    print_module_info(vertexai)
    
    # Print agent_engines module info
    print_module_info(vertexai.agent_engines)
    
    # Check agent engines methods
    check_agent_engine_methods()

if __name__ == "__main__":
    main()