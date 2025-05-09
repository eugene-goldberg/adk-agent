#!/usr/bin/env python3
"""
Script to update the agent ID in the truck_sharing_api.py file.
"""

import os
import re

def update_agent_id():
    """Update the DEFAULT_RESOURCE_ID in truck_sharing_api.py."""
    file_path = "./web_app/truck_sharing_api.py"
    new_agent_id = "1369314189046185984"
    
    print(f"Updating agent ID to {new_agent_id} in {file_path}")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update the DEFAULT_RESOURCE_ID in the file
    pattern = r'DEFAULT_RESOURCE_ID\s*=\s*os\.getenv\([^,]+,\s*"([^"]+)"\)'
    updated_content = re.sub(pattern, f'DEFAULT_RESOURCE_ID = os.getenv("TRUCK_AGENT_RESOURCE_ID", "{new_agent_id}")', content)
    
    with open(file_path, 'w') as f:
        f.write(updated_content)
    
    print("File updated successfully!")
    
    # Also set the environment variable
    os.environ["TRUCK_AGENT_RESOURCE_ID"] = new_agent_id
    print(f"Set environment variable TRUCK_AGENT_RESOURCE_ID to {new_agent_id}")

if __name__ == "__main__":
    update_agent_id()