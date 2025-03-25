from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import google.generativeai as genai
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configure API keys
os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDDkEk07-Y9ISJXKTWyJBArz19mYXMPEwM"

# Dynamically determine the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure BACKEND_DIR points to the correct backend directory
if BASE_DIR.endswith("backend"):
    BACKEND_DIR = BASE_DIR  # BASE_DIR already points to the backend directory
else:
    BACKEND_DIR = os.path.join(BASE_DIR, "backend")

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get('query', '').lower()

    # Load incidents from the sample_incidents.json file
    try:
        incidents_file = os.path.join(BACKEND_DIR, 'sample_incidents.json')
        with open(incidents_file, 'r') as file:
            incidents = json.load(file)
    except Exception as e:
        return jsonify({"error": f"Failed to load incidents: {str(e)}"}), 500

    # Prepare context for the model
    context = ""
    for incident in incidents:
        context += f"Incident ID: {incident.get('incident_id')}\n"
        context += f"Issue: {incident.get('issue')}\n"
        context += f"Application Affected: {incident.get('application_affected')}\n"
        context += f"Priority: {incident.get('priority')}\n"
        context += f"Upstream: {incident.get('upstream', 'None')}\n"
        context += f"Downstream: {incident.get('downstream', 'None')}\n\n"

    # Call Gemini model
    try:
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

        prompt = f"""
You are an expert IT analyst. Based on the following incident data, answer the user's query:

Incident Data:
{context}

User Query:
{query}

Provide a concise and accurate response. If no relevant incidents are found, explicitly state that there are no issues reported for the queried component or application.
"""
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 300,
        }
        model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
        response = model.generate_content(prompt)
        response_text = response.text.strip()
    except Exception as e:
        response_text = f"Error processing query with the Gemini model: {str(e)}"

    # Log the query and response
    print(f"Query: {query}")
    print(f"Response: {response_text}")

    return jsonify({"response": response_text})

@app.route('/heal', methods=['POST'])
def handle_heal():
    data = request.json
    issue_description = data.get('issue_description', 'No issue description provided.')

    try:
        # Call runbook.py with the issue description
        runbook_script = os.path.join(BACKEND_DIR, 'runbook.py')
        result = subprocess.run(
            ['python', runbook_script, issue_description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "runbook.md"  # Default output file name
            return jsonify({"status": "success", "output": result.stdout, "file": output_file, "path": os.path.join(BACKEND_DIR, output_file)})
        else:
            return jsonify({"status": "error", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/generate_runbook', methods=['POST'])
def generate_runbook():
    data = request.json
    issue_description = data.get('issue_description', 'No issue description provided.')

    try:
        # Call runbook.py with the issue description
        runbook_script = os.path.join(BACKEND_DIR, 'runbook.py')
        result = subprocess.run(
            ['python', runbook_script, issue_description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "runbook.md"  # Default output file name
            return jsonify({"status": "success", "output": result.stdout, "file": output_file, "path": os.path.join(BACKEND_DIR, output_file)})
        else:
            # Check if the error is due to both models failing
            if "Both OpenAI and Gemini models are unavailable" in result.stdout or "Unable to generate runbook" in result.stdout:
                return jsonify({"status": "error", "error": "Both models failed. Unable to generate runbook."}), 500
            return jsonify({"status": "error", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/generate_heal_script', methods=['POST'])
def generate_heal_script():
    data = request.json
    issue_description = data.get('issue_description', 'No issue description provided.')  # Issue description received here

    # Log the issue description being passed to heal_agent.py
    print(f"Issue description passed to heal_agent.py: {issue_description}")

    try:
        # Call heal_agent.py with the issue description
        heal_script = os.path.join(BACKEND_DIR, 'heal_agent.py')
        result = subprocess.run(
            ['python', heal_script, issue_description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "heal_script.sh"  # Default output file name
            return jsonify({"status": "success", "output": result.stdout, "file": output_file, "path": os.path.join(BACKEND_DIR, output_file)})
        else:
            return jsonify({"status": "error", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/incidents', methods=['GET'])
def get_incidents():
    try:
        # Serve the sample_incidents.json file
        print(f"Serving incidents from: {os.path.join(BACKEND_DIR, 'sample_incidents.json')}")  # Log the full path
        return send_from_directory(
            directory=BACKEND_DIR,  # Ensure this points to the backend directory
            path='sample_incidents.json',
            as_attachment=False
        )
    except Exception as e:
        print(f"Error serving /incidents: {str(e)}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/change_requests', methods=['GET'])
def get_change_requests():
    try:
        # Serve the sample_change_requests.json file
        print(f"Serving change requests from: {os.path.join(BACKEND_DIR, 'sample_change_requests.json')}")  # Log the full path
        return send_from_directory(
            directory=BACKEND_DIR,  # Ensure this points to the backend directory
            path='sample_change_requests.json',
            as_attachment=False
        )
    except Exception as e:
        print(f"Error serving /change_requests: {str(e)}")  # Log the error for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/cr_tracker', methods=['POST'])
def cr_tracker():
    data = request.json
    incident = data.get('incident', {})
    change_requests = data.get('change_requests', [])

    # Log missing data for debugging
    if not incident:
        print("Error: Incident details are missing in the request payload.")
    if not change_requests:
        print("Error: Change requests are missing in the request payload.")

    if not incident or not change_requests:
        return jsonify({"error": "Incident details or change requests are missing."}), 400

    try:
        # Call the cr_analysis_agent.py script
        import subprocess
        import json
        cr_analysis_script = os.path.join(BACKEND_DIR, 'cr_analysis_agent.py')
        result = subprocess.run(
            [
                'python',
                cr_analysis_script,
                json.dumps(incident),
                json.dumps(change_requests)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return jsonify({"impact_analysis": result.stdout.strip()})
        else:
            print(f"Error from cr_analysis_agent.py: {result.stderr.strip()}")
            return jsonify({"error": result.stderr.strip()}), 500
    except Exception as e:
        print(f"Exception in /cr_tracker: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/apps_affected', methods=['POST'])
def apps_affected():
    data = request.json
    incident_id = data.get('incident_id', None)

    if not incident_id:
        return jsonify({"error": "Incident ID is missing."}), 400

    try:
        # Call mcp_integration.py with the incident ID
        mcp_integration_script = os.path.join(BACKEND_DIR, 'mcp_integration.py')
        result = subprocess.run(
            ['python', mcp_integration_script, incident_id],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return jsonify({"apps_affected_analysis": result.stdout.strip()})
        else:
            print(f"Error from mcp_integration.py: {result.stderr.strip()}")  # Log the error
            return jsonify({"error": result.stderr.strip()}), 500
    except Exception as e:
        print(f"Exception in /apps_affected: {str(e)}")  # Log the exception
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

