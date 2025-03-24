import os
import sys
import google.generativeai as genai
from typing import Optional
from datetime import datetime

# Hardcode the API keys
os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyDDkEk07-Y9ISJXKTWyJBArz19mYXMPEwM"

def analyze_cr_with_model(incident_details, change_requests, openai_api_key=None, gemini_api_key=None, openai_model="gpt-3.5-turbo"):
    """
    Analyze the incident and change requests using Gemini models.

    Args:
        incident_details (dict): Details of the incident.
        change_requests (list): List of change requests.
        openai_api_key (str, optional): OpenAI API key (disabled for now).
        gemini_api_key (str, optional): Gemini API key.
        openai_model (str): OpenAI model to use (disabled for now).

    Returns:
        str: Analysis result from the model.
    """
    # Validate and filter change requests based on multiple parameters
    try:
        incident_start_date = datetime.fromisoformat(incident_details.get('start_date'))
    except ValueError:
        return "Invalid incident start date format. Please provide a valid ISO 8601 date."

    incident_issue = incident_details.get('issue', '').lower()
    incident_components = set(incident_details.get('application_affected', '').lower().split(','))
    filtered_change_requests = []

    for cr in change_requests:
        try:
            cr_date = datetime.fromisoformat(cr['implementation_date'])
        except ValueError:
            continue  # Skip CRs with invalid date formats

        cr_description = cr['description'].lower()
        cr_components = set(map(str.lower, cr['affected_components']))

        # Check date correlation (within 7 days before the incident)
        date_relevant = (incident_start_date - cr_date).days <= 7 and (incident_start_date - cr_date).days >= 0

        # Check if the issue description matches or is relevant to the CR description
        description_relevant = any(keyword in cr_description for keyword in incident_issue.split())

        # Check if affected components overlap
        components_relevant = bool(incident_components & cr_components)

        # Include the CR if it meets all three criteria
        if date_relevant and description_relevant and components_relevant:
            filtered_change_requests.append(cr)

    if not filtered_change_requests:
        return "No change requests are relevant to this incident based on the provided details."

    # Prepare the prompt
    prompt = f"""
You are an expert IT analyst. Analyze the following incident and change requests to determine which changes might have caused or impacted the incident.

Incident Details:
- **Issue**: {incident_details.get('issue')}
- **Application Affected**: {incident_details.get('application_affected')}
- **Start Date**: {incident_details.get('start_date')}
- **Priority**: {incident_details.get('priority')}

Change Requests:
"""
    for cr in filtered_change_requests:
        prompt += f"""
- **Change ID**: {cr['change_id']}
  - **Description**: {cr['description']}
  - **Affected Components**: {', '.join(cr['affected_components'])}
  - **Implementation Date**: {cr['implementation_date']}
"""

    prompt += """
Analyze the incident and change requests. Identify which change requests might have caused or impacted the incident. Provide a detailed explanation for each identified change request.

**Output Format**:
###  Change Requests that could've led to this incident
- **Change ID**: <Change ID>  
  - **Reason for Impact**: <Reason>  
  - **Timing Correlation**: <Timing>  
  - **Affected Components**: <Components>  

Ensure the output is strictly based on the provided data. Do not make assumptions about incorrect or missing data. Avoid hypothetical scenarios.
"""

    # Commenting out OpenAI-related code
    # if openai_api_key:
    #     try:
    #         import openai
    #         openai.api_key = openai_api_key

    #         response = openai.ChatCompletion.create(
    #             model=openai_model,
    #             messages=[
    #                 {"role": "system", "content": "You are an expert IT analyst."},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             max_tokens=1000,
    #             temperature=0.7
    #         )
    #         return response['choices'][0]['message']['content'].strip()
    #     except Exception as e:
    #         # Log the error for debugging but suppress it from the output
    #         print(f"OpenAI model failed: {str(e)}")

    # Use Gemini
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
            return response.text.strip()
        except Exception as e:
            # Log the error for debugging but suppress it from the output
            print(f"Gemini model failed: {str(e)}")

    return "Gemini model failed to analyze the incident and change requests."

def analyze_cr(incident_details, change_requests):
    """
    Analyze the incident and change requests to determine potential impacts.

    Args:
        incident_details (dict): Details of the incident.
        change_requests (list): List of change requests.

    Returns:
        str: Analysis result.
    """
    return analyze_cr_with_model(
        incident_details=incident_details,
        change_requests=change_requests,
        gemini_api_key=os.environ.get("GOOGLE_API_KEY")
    )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Incident details and change requests must be provided.")
        sys.exit(1)

    import json

    # Parse incident details and change requests from command-line arguments
    incident_details = json.loads(sys.argv[1])
    change_requests = json.loads(sys.argv[2])

    try:
        analysis_result = analyze_cr(incident_details, change_requests)
        print(f"Analysis Result:\n{analysis_result}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)
