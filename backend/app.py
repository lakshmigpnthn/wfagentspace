from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

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
        "rca": "Root Cause Analysis: Identified potential memory leak in worker threads."
    }
    
    response_text = "Query processed. No specific information available for this request."
    for key, value in responses.items():
        if key in query:
            response_text = value
            break
    
    if "help" in query:
        response_text = "Available commands: check memory, check cpu, check network, check errors, check status, heal application, run rca"
    
    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)

