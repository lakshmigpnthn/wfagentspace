import os
import sys
import time
import json
import requests
import google.generativeai as genai

# Hardcode the API keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyALENrXIslUHsrTlwHqV_qpItxC17J08co"
os.environ["OPENAI_API_KEY"] = "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"

def download_file_from_gcs(url, output_file):
    """
    Download a file from a GCS bucket using its public URL.

    Args:
        url (str): The public URL of the file in the GCS bucket.
        output_file (str): The local file path to save the downloaded file.

    Returns:
        str: Path to the downloaded file.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for HTTP issues

        # Write the content to a local file
        with open(output_file, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return output_file
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        sys.exit(1)

def analyze_apps_affected(incident_id, context_data, gemini_api_key=None, openai_api_key=None):
    """
    Analyze the applications affected by the incident using Gemini or OpenAI models.

    Args:
        incident_id (str): The ID of the incident.
        context_data (dict): JSON data containing upstream/downstream details.
        gemini_api_key (str, optional): Gemini API key.
        openai_api_key (str, optional): OpenAI API key.

    Returns:
        str: Analysis result from the model in a consistent format.
    """
    # Filter the context data to include only the specific incident
    filtered_context = [incident for incident in context_data if incident.get("incident_id") == incident_id]

    if not filtered_context:
        return f"No data found for Incident ID: {incident_id}"

    # Extract the specific incident details
    incident_details = filtered_context[0]

    # Add placeholders for upstream and downstream if missing
    upstream = incident_details.get("upstream", "No upstream applications are impacted by this incident.")
    downstream = incident_details.get("downstream", "No downstream applications are impacted by this incident.")

    # Prepare the prompt
    prompt = f"""
You are an expert IT analyst. Analyze the following incident and determine the upstream and downstream applications affected:

Incident ID: {incident_id}

Context Data:
- Upstream: {upstream}
- Downstream: {downstream}

The analysis should include:
1. Affected upstream applications.
2. Affected downstream applications.

If no upstream or downstream applications are impacted, explicitly state so. Do not assume or provide additional information if data is missing or incomplete. Avoid including recommendations or further analysis.

Provide the output in the following format:
---
Applications affected by Incident ID: <Incident ID>

**Upstream Applications:**
- <List of upstream applications or "No upstream applications are impacted.">

**Downstream Applications:**
- <List of downstream applications or "No downstream applications are impacted.">
---
"""

    # Try Gemini API first
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)

            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1000,
            }
            model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
            response = model.generate_content(prompt)
            return format_response(incident_id, response.text.strip())
        except Exception as e:
            print(f"Gemini model failed: {str(e)}")

    # Fallback to OpenAI API
    if openai_api_key:
        try:
            import openai
            openai.api_key = openai_api_key

            response = openai.Completion.create(
                engine="gpt-3.5-turbo",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            return format_response(incident_id, response.choices[0].text.strip())
        except Exception as e:
            print(f"OpenAI model failed: {str(e)}")

    return "Both Gemini and OpenAI models failed to analyze the applications affected."

def format_response(incident_id, model_response):
    """
    Format the model's response to ensure a consistent structure.

    Args:
        incident_id (str): The ID of the incident.
        model_response (str): The raw response from the model.

    Returns:
        str: Formatted response.
    """
    # Remove redundant headers from the model's response
    cleaned_response = model_response.replace(f"Applications affected by Incident ID: {incident_id}", "").strip()

    # Add the header if it's not already included
    return f"""
Upstream/Downstream Applications affected by Incident ID: {incident_id}

{cleaned_response}
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No incident ID provided.")
        sys.exit(1)

    incident_id = sys.argv[1]  # Take incident ID from the command-line argument
    gcs_url = "https://storage.googleapis.com/store-anything/sample_incidents.json"
    local_file = "sample_incidents.json"

    try:
        # Download the JSON file from the GCS bucket
        downloaded_file = download_file_from_gcs(gcs_url, local_file)

        # Load the JSON data from the downloaded file
        with open(downloaded_file, "r") as file:
            context_data = json.load(file)

        # Analyze the applications affected
        analysis_result = analyze_apps_affected(
            incident_id=incident_id,
            context_data=context_data,
            gemini_api_key=os.environ.get("GOOGLE_API_KEY"),
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        print(analysis_result)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)