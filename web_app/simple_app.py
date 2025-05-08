#!/usr/bin/env python3
"""
Simple Flask app to test the agent API endpoints.
"""

from flask import Flask, jsonify, request, render_template_string
import os
import re
import subprocess
import sys
import time

app = Flask(__name__)

# Constants
PROJECT_ID = "pickuptruckapp"
REGION = "us-central1"
AGENT_ID = "1818126039411326976"
RESOURCE_ID = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{AGENT_ID}"

# Set the proper Python path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# HTML template for the test page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Agent API Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        .section { margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { padding: 8px 16px; background-color: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer; }
        pre { background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
        input[type="text"] { width: 70%; padding: 8px; margin-right: 10px; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Agent API Test Interface</h1>
        
        <div class="section">
            <h2>Agent Information</h2>
            <p><strong>Agent ID:</strong> {{ agent_id }}</p>
            <p><strong>Resource ID:</strong> {{ resource_id }}</p>
        </div>
        
        <div class="section">
            <h2>Create Session</h2>
            <button id="createSessionBtn" class="btn">Create Session</button>
            <div id="sessionResult"></div>
        </div>
        
        <div class="section">
            <h2>Send Message</h2>
            <div>
                <input type="text" id="sessionId" placeholder="Session ID" />
            </div>
            <div style="margin-top: 10px;">
                <input type="text" id="message" placeholder="Your message" />
                <button id="sendMessageBtn" class="btn">Send</button>
            </div>
            <div id="messageResult"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('createSessionBtn').addEventListener('click', async () => {
            const resultDiv = document.getElementById('sessionResult');
            resultDiv.innerHTML = '<p>Creating session...</p>';
            
            try {
                const response = await fetch('/api/create_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resource_id: '{{ resource_id }}' })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <p class="success">Session created successfully!</p>
                        <p><strong>Session ID:</strong> ${data.session_id}</p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                    
                    // Auto-fill the session ID field
                    document.getElementById('sessionId').value = data.session_id;
                } else {
                    resultDiv.innerHTML = `
                        <p class="error">Failed to create session</p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            }
        });
        
        document.getElementById('sendMessageBtn').addEventListener('click', async () => {
            const sessionId = document.getElementById('sessionId').value;
            const message = document.getElementById('message').value;
            const resultDiv = document.getElementById('messageResult');
            
            if (!sessionId || !message) {
                resultDiv.innerHTML = '<p class="error">Session ID and message are required</p>';
                return;
            }
            
            resultDiv.innerHTML = '<p>Sending message...</p>';
            
            try {
                const response = await fetch('/api/send_message', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        resource_id: '{{ resource_id }}',
                        session_id: sessionId,
                        message: message
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <p class="success">Message sent successfully!</p>
                        <p><strong>Response:</strong></p>
                        <div style="white-space: pre-wrap; background-color: #f5f5f5; padding: 10px; border-radius: 4px;">${data.response}</div>
                        <p><strong>Raw output:</strong></p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <p class="error">Failed to send message</p>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
"""

def run_command(command):
    """Run a shell command with proper environment variables."""
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH', '')}"
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            env=env
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout if result.stdout else "",
            "stderr": result.stderr if result.stderr else "",
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        }

def extract_session_id(output):
    """Extract session ID from command output."""
    if not output:
        return None
    match = re.search(r'Session ID: (\d+)', output)
    if match:
        return match.group(1)
    return None

@app.route('/')
def index():
    """Render the test interface."""
    return render_template_string(HTML_TEMPLATE, 
                                 agent_id=AGENT_ID, 
                                 resource_id=RESOURCE_ID)

@app.route('/api/create_session', methods=['POST'])
def create_session():
    """Create a session with a Vertex AI agent."""
    try:
        data = request.json or {}
        resource_id = data.get('resource_id', RESOURCE_ID)
        
        # Run the command to create a session
        command = f"cd {PROJECT_ROOT} && python3 deployment/customer_service_remote.py --create_session --resource_id={resource_id}"
        result = run_command(command)
        
        # Debug information
        print("Create session command:", command)
        print("Command output:", result)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to create session",
                "details": result["stderr"] or "Unknown error",
                "command": command
            }), 500
        
        # Extract the session ID from the output
        session_id = extract_session_id(result["stdout"])
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Failed to extract session ID from output",
                "output": result["stdout"],
                "command": command
            }), 500
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "resource_id": resource_id,
            "output": result["stdout"]
        })
    
    except Exception as e:
        print("Error in create_session:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """Send a message to a Vertex AI agent session."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        resource_id = data.get('resource_id', RESOURCE_ID)
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Session ID is required"
            }), 400
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Run the command to send a message
        command = f'cd {PROJECT_ROOT} && python3 deployment/customer_service_remote.py --send --resource_id={resource_id} --session_id={session_id} --message="{message}"'
        result = run_command(command)
        
        # Debug information
        print("Send message command:", command)
        print("Command output length:", len(result["stdout"]))
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to send message",
                "details": result["stderr"] or "Unknown error",
                "command": command
            }), 500
        
        # Extract the response from the output
        output = result["stdout"]
        
        # Try to extract the response content from the JSON output
        try:
            # Look for text content in the output
            text_matches = re.findall(r'"text": "([^"]*)"', output)
            
            if text_matches:
                # Join all text matches
                response_content = "\n".join([text.replace('\\n', '\n').replace('\\\"', '"') for text in text_matches])
            else:
                response_content = "No response text found in the output"
            
            return jsonify({
                "success": True,
                "response": response_content,
                "raw_output": output[:1000] + "..." if len(output) > 1000 else output  # Truncate for readability
            })
        except Exception as e:
            return jsonify({
                "success": True,
                "response": "Could not parse response content",
                "raw_output": output[:1000] + "..." if len(output) > 1000 else output,
                "parse_error": str(e)
            })
    
    except Exception as e:
        print("Error in send_message:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the agent API test app')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    print(f"Starting server on port {args.port}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Resource ID: {RESOURCE_ID}")
    
    app.run(debug=True, port=args.port)