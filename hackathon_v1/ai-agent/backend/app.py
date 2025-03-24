from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import google.generativeai as genai
import openai

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configure API keys
os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDDkEk07-Y9ISJXKTWyJBArz19mYXMPEwM"

@app.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get('query', '').lower()
    
    responses = {
        "memory": "Current memory usage is at 78% with 3.2GB available. No memory leaks detected in the last 24 hours.",
        "cpu": "CPU utilization at 45% with occasional spikes to 82% during peak traffic hours (14:00-16:00).",
        "network": "Network throughput stable at 1.2Gbps. No packet loss detected on primary interfaces.",
        "errors": "12 error events logged in the last hour. Most common: 'Connection timeout' (8 occurrences).",
        "status": "The application is currently in a warning state with 4 instances running.",
        "heal": "Initiated healing process. Memory optimization in progress.",
        "rca": "Root Cause Analysis: Identified potential memory leak in worker threads.",
        "pod" : "The pod is killed due to Out Of Memory (OOM) errors in namespace ai_np, meaning the node doesn't have enough resources to run the pod"
    }
    
    response_text = "Query processed. No specific information available for this request."
    for key, value in responses.items():
        if key in query:
            response_text = value
            break
    
    if "help" in query:
        response_text = "Available commands: check memory, check cpu, check network, check errors, check status, heal application, run rca"
    
    # Log the issue description being passed to runbook.py
    print(f"Issue description passed to runbook.py: {response_text}")
    
    # Trigger runbook generation using the response text as the issue description
    try:
        result = subprocess.run(
            ['python', 'f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backendrunbook.py', response_text],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "runbook.md"
            return jsonify({
                "response": response_text,
                "runbook_status": "success",
                "runbook_file": output_file,
                "runbook_path": f"f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\{output_file}"
            })
        else:
            return jsonify({
                "response": response_text,
                "runbook_status": "error",
                "runbook_error": result.stderr
            })
    except Exception as e:
        return jsonify({
            "response": response_text,
            "runbook_status": "error",
            "runbook_error": str(e)
        })

@app.route('/heal', methods=['POST'])
def handle_heal():
    data = request.json
    issue_description = data.get('issue_description', 'No issue description provided.')

    try:
        # Call runbook.py with the issue description
        result = subprocess.run(
            ['python', 'f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\runbook.py', issue_description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "runbook.md"  # Default output file name
            return jsonify({"status": "success", "output": result.stdout, "file": output_file, "path": f"f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\{output_file}"})
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
        result = subprocess.run(
            ['python', 'f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backend\\runbook.py', issue_description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "runbook.md"  # Default output file name
            return jsonify({"status": "success", "output": result.stdout, "file": output_file, "path": f"f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\{output_file}"})
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
        result = subprocess.run(
            ['python', 'f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backend\\heal_agent.py', issue_description],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output_file = "heal_script.sh"  # Default output file name
            return jsonify({"status": "success", "output": result.stdout, "file": output_file, "path": f"f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backend\\{output_file}"})
        else:
            return jsonify({"status": "error", "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/incidents', methods=['GET'])
def get_incidents():
    try:
        # Serve the sample_incidents.json file
        return send_from_directory(
            directory='f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backend\\',
            path='sample_incidents.json',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/change_requests', methods=['GET'])
def get_change_requests():
    try:
        # Serve the sample_change_requests.json file
        return send_from_directory(
            directory='f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backend\\',
            path='sample_change_requests.json',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cr_tracker', methods=['POST'])
def cr_tracker():
    data = request.json
    incident = data.get('incident', {})
    change_requests = data.get('change_requests', [])

    if not incident or not change_requests:
        return jsonify({"error": "Incident details or change requests are missing."}), 400

    try:
        # Call the cr_analysis_agent.py script
        import subprocess
        import json
        result = subprocess.run(
            [
                'python',
                'f:\\study\\hackathon\\testing-module\\wfagentspace\\hackathon_v1\\ai-agent\\backend\\cr_analysis_agent.py',
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

if __name__ == '__main__':
    app.run(debug=True)

