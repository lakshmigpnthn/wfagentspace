import os
import sys
import google.generativeai as genai
from typing import Optional

# Hardcode the API keys
os.environ["OPENAI_API_KEY"] = "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"
os.environ["GOOGLE_API_KEY"] = "AIzaSyALENrXIslUHsrTlwHqV_qpItxC17J08co"

def generate_heal_script_with_model(issue_description, openai_api_key=None, gemini_api_key=None, openai_model="gpt-3.5-turbo"):
    """
    Generate a shell script to solve the issue using OpenAI or Gemini models.

    Args:
        issue_description (str): Description of the issue.
        openai_api_key (str, optional): OpenAI API key.
        gemini_api_key (str, optional): Gemini API key.
        openai_model (str): OpenAI model to use.

    Returns:
        str: Generated shell script content.
    """
    # Use OpenAI if API key is provided
    if openai_api_key:
        try:
            import openai
            openai.api_key = openai_api_key

            prompt = f"""
You are an expert DevOps engineer. Based on the following issue description, generate a shell script to resolve the issue:

Issue Description:
{issue_description}

The shell script should:
1. Stop any affected services.
2. Apply necessary fixes.
3. Restart the services.
4. Include comments explaining each step.

Provide the script in a format that can be directly executed on a Linux system.
"""
            response = openai.Completion.create(
                engine=openai_model,
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"OpenAI model failed: {str(e)}")

    # Fallback to Gemini if OpenAI fails
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)

            prompt = f"""
You are an expert DevOps engineer. Based on the following issue description, generate a shell script to resolve the issue:

Issue Description:
{issue_description}

The shell script should:
1. Stop any affected services.
2. Apply necessary fixes.
3. Restart the services.
4. Include comments explaining each step.

Provide the script in a format that can be directly executed on a Linux system.
"""
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 500,
            }
            model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini model failed: {str(e)}")

    raise RuntimeError("Both OpenAI and Gemini models failed to generate the heal script.")

def generate_heal_script(issue_description):
    """
    Generate a shell script to solve the issue based on the issue description.

    Args:
        issue_description (str): Description of the issue.

    Returns:
        str: Path to the generated script file.
    """
    script_content = generate_heal_script_with_model(
        issue_description=issue_description,
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
        gemini_api_key=os.environ.get("GOOGLE_API_KEY"),
        openai_model="gpt-3.5-turbo"
    )

    output_file = "heal_script.sh"
    with open(output_file, "w") as f:
        f.write(script_content)
    
    # Make the script executable
    os.chmod(output_file, 0o755)

    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No issue description provided.")
        sys.exit(1)

    issue_description = sys.argv[1]  # Issue description received here
    try:
        output_file = generate_heal_script(issue_description)
        print(f"Heal script created successfully at: {output_file}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)
