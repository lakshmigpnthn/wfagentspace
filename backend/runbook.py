import os
import google.generativeai as genai
from typing import Optional

def create_runbook_from_steps(
    issue_description: str, 
    output_file: str = "runbook.md", 
    gemini_api_key: Optional[str] = None
):
    """
    Create a runbook from identified fix steps using Google's Gemini 1.5 Pro.
    
    Args:
        issue_description (str): Description of the issue and identified fix steps
        output_file (str): File path to save the generated runbook
        gemini_api_key (str, optional): Google Gemini API key
    
    Returns:
        str: Path to the saved runbook file
    """
    # Set up the API key for Gemini
    if gemini_api_key:
        os.environ["GOOGLE_API_KEY"] = gemini_api_key
    elif not os.environ.get("GOOGLE_API_KEY"):
        raise ValueError("Google API key not provided")
    
    # Initialize the Google Generative AI library
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    # Configure the model - specifically using gemini-1.5-pro
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    
    # Create the model instance
    model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)
    
    print("Creating runbook using gemini-1.5-pro...")
    
    # System prompts for each agent role
    analyst_prompt = """You are an expert IT analyst who can understand technical issues deeply.
Your task is to analyze the issue description, identify the root cause, and ensure all necessary fix steps are properly understood."""

    writer_prompt = """You are an expert technical writer who specializes in creating clear, structured runbooks.
Your job is to transform an analyzed issue and fix steps into a professional, comprehensive runbook.
The runbook should include:
1. Title and executive summary
2. Detailed issue description and impact
3. Prerequisites (tools, access, credentials needed)
4. Step-by-step implementation instructions with clear formatting
5. Verification procedures to confirm the fix worked
6. Rollback instructions if needed
7. Troubleshooting section for common issues
Format the output in markdown for easy reading and future reference."""

    reviewer_prompt = """You are an experienced IT operations specialist who reviews runbooks for accuracy and completeness.
Make sure that:
1. All steps are technically accurate and in the correct order
2. No critical steps are missing
3. Prerequisites are complete
4. Verification steps will effectively confirm the fix
5. Edge cases and potential issues are addressed"""

    formatter_prompt = """You are a document formatting specialist who ensures runbooks are properly structured and formatted.
Ensure that:
1. The markdown formatting is consistent and professional
2. Headers are properly nested and follow a logical structure
3. Code blocks, tables, and lists are properly formatted
4. The document has a professional appearance and is easy to read
5. The final document is ready for distribution to IT staff"""
    
    # Step 1: Analyze the issue
    print("Step 1: Analyzing the issue...")
    analysis_prompt = f"{analyst_prompt}\n\nPlease analyze this issue:\n\n{issue_description}"
    analysis_response = model.generate_content(analysis_prompt)
    issue_analysis = analysis_response.text
    
    # Step 2: Create initial runbook draft
    print("Step 2: Creating initial runbook draft...")
    runbook_prompt = f"{writer_prompt}\n\nHere is the issue analysis:\n{issue_analysis}\n\nHere is the original issue description:\n{issue_description}\n\nPlease create a comprehensive runbook based on this information."
    runbook_response = model.generate_content(runbook_prompt)
    initial_runbook = runbook_response.text
    
    # Step 3: Technical review
    print("Step 3: Performing technical review...")
    review_prompt = f"{reviewer_prompt}\n\nPlease review this runbook:\n{initial_runbook}\n\nProvide specific feedback for improvements."
    review_response = model.generate_content(review_prompt)
    review_feedback = review_response.text
    
    # Step 4: Final formatting and improvements
    print("Step 4: Finalizing format and improvements...")
    final_prompt = f"{formatter_prompt}\n\nHere is the runbook draft:\n{initial_runbook}\n\nHere is the technical review feedback:\n{review_feedback}\n\nPlease provide the final, formatted runbook in clean markdown format."
    final_response = model.generate_content(final_prompt)
    final_runbook = final_response.text
    
    # Save the final runbook to a file
    with open(output_file, "w") as f:
        f.write(final_runbook)
    
    print(f"Runbook created and saved to '{output_file}'")
    return output_file

# Example usage
if __name__ == "__main__":
    # Example issue description with fix steps
    example_issue = """
    Issue: Application server crashes under high load
    
    Description:
    The web application server crashes when user load exceeds 500 concurrent users.
    Server logs show "Out of Memory" errors before each crash.
    The issue began after deploying the latest feature update last week.
    
    Fix Steps Identified:
    1. Increase server memory allocation
       - Update JVM heap settings from 2GB to 4GB
       - Modify server configuration in /etc/appserver/config.xml
    
    2. Implement connection throttling
       - Configure max connection limit to 400
       - Set up request queuing for excess connections
    
    3. Fix memory leak in user session handling
       - Patch the UserSessionManager.java file
       - Add proper session timeout and cleanup
    
    4. Add monitoring and alerts
       - Deploy memory usage monitors
       - Set up alerts at 80% memory utilization
    
    5. Create load balancing configuration
       - Set up additional application server instance
       - Configure load balancer to distribute traffic
    """
    
    try:
        # Create the runbook using Gemini 1.5 Pro
        output_file = create_runbook_from_steps(
            issue_description=example_issue,
            output_file="server_crash_runbook.md",
            gemini_api_key="AIzaSyCqNI95axOXHF53c4SDtElyZ75F__mMKwY"  # Your API key
        )
        print(f"Runbook created successfully at: {output_file}")
        
        # Display the contents of the created file
        with open(output_file, 'r') as f:
            print("\nRunbook contents:")
            print(f.read())
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")