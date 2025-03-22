import os
import autogen
from typing import Optional
import google.generativeai as genai

def create_runbook_from_steps(
    issue_description: str, 
    output_file: str = "runbook.md", 
    gemini_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-3.5-turbo"
):
    """
    Create a runbook from identified fix steps using AutoGen agents with OpenAI.
    
    Args:
        issue_description (str): Description of the issue and identified fix steps
        output_file (str): File path to save the generated runbook
        gemini_api_key (str, optional): Google Gemini API key for fallback
        openai_api_key (str, optional): OpenAI API key for AutoGen agents
        openai_model (str): The OpenAI model to use, default is "gpt-3.5-turbo"
    
    Returns:
        str: Path to the saved runbook file
    """
    # Set up the API key for OpenAI (required for AutoGen)
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    elif not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OpenAI API key not provided. AutoGen requires an OpenAI API key.")
    
    # Also set up Gemini API key for fallback
    if gemini_api_key:
        os.environ["GOOGLE_API_KEY"] = gemini_api_key
    
    # Configuration for AutoGen with OpenAI
    config_list = [
        {
            "model": openai_model,
            "api_key": os.environ.get("OPENAI_API_KEY")
        }
    ]
    
    llm_config = {
        "config_list": config_list,
        "temperature": 0.7,
    }
    
    print(f"Creating runbook using AutoGen agents with {openai_model}...")
    
    # Create a user proxy agent that will orchestrate the process
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=10,
        system_message="You are a user who needs help creating a runbook for fixing technical issues.",
        code_execution_config={
            "work_dir": ".",
            "use_docker": False,
        },
    )
    
    # Create an analyst agent to understand and structure the issue
    analyst = autogen.AssistantAgent(
        name="Analyst",
        system_message="""You are an expert IT analyst who can understand technical issues deeply.
Your task is to analyze the issue description, identify the root cause, and ensure all necessary fix steps are properly understood.
You should ask clarifying questions if needed and ensure the problem is fully defined before proceeding with the runbook creation.""",
        llm_config=llm_config,
    )
    
    # Create a runbook writer agent
    runbook_writer = autogen.AssistantAgent(
        name="RunbookWriter",
        system_message="""You are an expert technical writer who specializes in creating clear, structured runbooks.
Your job is to take the analyzed issue and fix steps and transform them into a professional, comprehensive runbook.
The runbook should include:
1. Title and executive summary
2. Detailed issue description and impact
3. Prerequisites (tools, access, credentials needed)
4. Step-by-step implementation instructions with clear formatting
5. Verification procedures to confirm the fix worked
6. Rollback instructions if needed
7. Troubleshooting section for common issues
Format the output in markdown for easy reading and future reference.""",
        llm_config=llm_config,
    )
    
    # Create a technical reviewer agent
    reviewer = autogen.AssistantAgent(
        name="TechnicalReviewer",
        system_message="""You are an experienced IT operations specialist who reviews runbooks for accuracy and completeness.
Your task is to review the runbook and ensure:
1. All steps are technically accurate and in the correct order
2. No critical steps are missing
3. Prerequisites are complete
4. Verification steps will effectively confirm the fix
5. Edge cases and potential issues are addressed
Provide specific feedback on improvements needed.""",
        llm_config=llm_config,
    )
    
    # Create a document formatter agent
    formatter = autogen.AssistantAgent(
        name="Formatter",
        system_message="""You are a document formatting specialist who ensures runbooks are properly structured and formatted.
Your task is to take the finalized runbook content and ensure:
1. The markdown formatting is consistent and professional
2. Headers are properly nested and follow a logical structure
3. Code blocks, tables, and lists are properly formatted
4. The document has a professional appearance and is easy to read
5. The final document is ready for distribution to IT staff
Provide the final formatted runbook in pristine markdown format.""",
        llm_config=llm_config,
    )
    
    # Create a group chat for all agents to collaborate
    groupchat = autogen.GroupChat(
        agents=[user_proxy, analyst, runbook_writer, reviewer, formatter],
        messages=[],
        max_round=20,
    )
    
    # Important: Set up the manager with LLM config for speaker selection
    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,  # This fixes the error about speaker selection agent
    )
    
    try:
        # Start the conversation with the issue description
        user_proxy.initiate_chat(
            manager,
            message=f"""
I need a comprehensive runbook created for the following issue and fix steps:

{issue_description}

Please work together to analyze this issue, create a detailed runbook, review it for technical accuracy, and format it professionally.

The process should be:
1. Analyst: Analyze the issue and ensure all fix steps are understood
2. RunbookWriter: Create the initial comprehensive runbook
3. TechnicalReviewer: Review for technical accuracy and completeness
4. Formatter: Ensure professional formatting and structure
5. All: Collaborate to refine the final document

The final runbook should be in markdown format and ready to be saved to {output_file}.
When the process is complete, Formatter should provide the final markdown document.
""",
        )
        
        # Extract the final runbook from the conversation
        messages = groupchat.messages
        final_runbook = None
        
        # Look for the formatter's final message
        for message in reversed(messages):
            if message["sender"] == "Formatter":
                content = message["content"]
                # Try to extract markdown content if it's in a code block
                if "```markdown" in content or "```" in content:
                    start_idx = content.find("```markdown")
                    if start_idx == -1:
                        start_idx = content.find("```")
                    if start_idx != -1:
                        start_idx = content.find("\n", start_idx) + 1
                        end_idx = content.rfind("```")
                        if end_idx != -1:
                            final_runbook = content[start_idx:end_idx].strip()
                            break
                else:
                    # If no markdown blocks, use the whole content
                    final_runbook = content
                    break
        
        # If no formatter message found, try to get the last substantial message
        if not final_runbook:
            for message in reversed(messages):
                if message["sender"] in ["RunbookWriter", "TechnicalReviewer", "Formatter"] and len(message["content"]) > 100:
                    final_runbook = message["content"]
                    break
                    
    except Exception as e:
        print(f"AutoGen processing failed: {str(e)}")
        print("Falling back to direct Gemini generation...")
        final_runbook = generate_with_gemini(issue_description)
    
    # If still no runbook, use a default message
    if not final_runbook:
        final_runbook = "# Error\nNo runbook was successfully generated. Please try again with more detailed fix steps."
    
    # Save the final runbook to a file
    with open(output_file, "w") as f:
        f.write(final_runbook)
    
    print(f"Runbook created and saved to '{output_file}'")
    return output_file

def generate_with_gemini(issue_description):
    """Fallback function to generate runbook using Gemini directly if AutoGen fails"""
    
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
    
    # Create a single comprehensive prompt
    prompt = f"""
You need to create a comprehensive runbook for the following issue:

{issue_description}

The runbook should include:
1. Title and executive summary
2. Detailed issue description and impact
3. Prerequisites (tools, access, credentials needed)
4. Step-by-step implementation instructions with clear formatting
5. Verification procedures to confirm the fix worked
6. Rollback instructions if needed
7. Troubleshooting section for common issues

Format the output in markdown for easy reading and future reference.
"""
    
    # Generate the runbook
    response = model.generate_content(prompt)
    return response.text

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
        # Create the runbook using AutoGen with OpenAI (and Gemini fallback)
        output_file = create_runbook_from_steps(
            issue_description=example_issue,
            output_file="server_crash_runbook.md",
            gemini_api_key="AIzaSyCqNI95axOXHF53c4SDtElyZ75F__mMKwY",  # Your Gemini API key for fallback
            openai_api_key="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",  # Replace with your actual OpenAI API key
            openai_model="gpt-3.5-turbo"  # Can use "gpt-4" for better results
        )
        print(f"Runbook created successfully at: {output_file}")
        
        # Display the contents of the created file
        with open(output_file, 'r') as f:
            print("\nRunbook contents:")
            print(f.read())
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")