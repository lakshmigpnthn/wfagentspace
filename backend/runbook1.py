import os
import autogen
from typing import Optional, List, Dict, Any
import google.generativeai as genai

# Create a custom agent that uses Gemini directly
class GeminiAgent(autogen.ConversableAgent):
    """
    A custom agent that directly uses Google's Gemini API.
    This agent extends AutoGen's ConversableAgent class but uses Gemini for generation.
    """
    
    def __init__(
        self,
        name: str,
        system_message: str,
        gemini_api_key: Optional[str] = None,
        model: str = "gemini-1.5-pro",
        **kwargs
    ):
        super().__init__(name=name, system_message=system_message, **kwargs)
        
        # Set up the API key for Gemini
        self.api_key = gemini_api_key or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key not provided")
        
        # Initialize the Google Generative AI library
        genai.configure(api_key=self.api_key)
        
        # Configure the model
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        # Create the model instance
        self.model = genai.GenerativeModel(model_name=model, generation_config=self.generation_config)
        self.model_name = model
        
        # Store conversation history
        self.conversation_history = {}
    
    def _generate_gemini_reply(self, messages: List[Dict[str, Any]], sender_name: str) -> str:
        """Generate a reply using Gemini based on the messages."""
        try:
            # Build a prompt that includes the system message and relevant conversation history
            prompt = f"You are {self.name}.\n\nSystem instruction: {self.system_message}\n\n"
            
            # Add conversation context (last few messages)
            message_history = messages[-5:] if len(messages) > 5 else messages
            for msg in message_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                prompt += f"{role}: {msg['content']}\n\n"
            
            # Add prompt for response
            prompt += f"You ({self.name}) should now respond to {sender_name}:"
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating response with Gemini: {str(e)}")
            return f"I encountered an error processing your message: {str(e)}"
    
    def generate_reply(
        self, messages: List[Dict[str, Any]], sender: autogen.Agent, **kwargs
    ) -> Optional[str]:
        """Override generate_reply to use Gemini for generation."""
        
        # Track conversation if this is a new sender
        sender_name = sender.name if sender else "User"
        if sender_name not in self.conversation_history:
            self.conversation_history[sender_name] = []
        
        # Format messages for Gemini
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })
        
        # Store in conversation history
        self.conversation_history[sender_name].extend(formatted_messages)
        
        # Generate the reply using Gemini
        reply = self._generate_gemini_reply(formatted_messages, sender_name)
        
        return reply

def create_runbook_from_steps(
    issue_description: str, 
    output_file: str = "runbook.md", 
    gemini_api_key: Optional[str] = None,
    model: str = "gemini-1.5-pro"
):
    """
    Create a runbook from identified fix steps using AutoGen with custom Gemini agents.
    
    Args:
        issue_description (str): Description of the issue and identified fix steps
        output_file (str): File path to save the generated runbook
        gemini_api_key (str, optional): Google Gemini API key
        model (str): The model to use, default is "gemini-1.5-pro"
    
    Returns:
        str: Path to the saved runbook file
    """
    # Set up the API key for Gemini
    if gemini_api_key:
        os.environ["GOOGLE_API_KEY"] = gemini_api_key
    elif not os.environ.get("GOOGLE_API_KEY"):
        raise ValueError("Google API key not provided")
    
    print(f"Creating runbook using AutoGen agents with Gemini {model}...")
    
    try:
        # Step 1: Create the agents
        # User proxy doesn't need to use Gemini, so we use the standard one
        user_proxy = autogen.UserProxyAgent(
            name="User",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=10,
            system_message="You are a user who needs help creating a runbook for fixing technical issues.",
            code_execution_config={"work_dir": ".", "use_docker": False},
        )
        
        # Create specialized Gemini agents
        analyst = GeminiAgent(
            name="Analyst",
            system_message="""You are an expert IT analyst who can understand technical issues deeply.
Your task is to analyze the issue description, identify the root cause, and ensure all necessary fix steps are properly understood.
You should provide a detailed analysis that identifies key problems, potential impacts, and validates the proposed fix steps.""",
            gemini_api_key=gemini_api_key,
            model=model
        )
        
        runbook_writer = GeminiAgent(
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
            gemini_api_key=gemini_api_key,
            model=model
        )
        
        reviewer = GeminiAgent(
            name="TechnicalReviewer",
            system_message="""You are an experienced IT operations specialist who reviews runbooks for accuracy and completeness.
Your task is to review the runbook and ensure:
1. All steps are technically accurate and in the correct order
2. No critical steps are missing
3. Prerequisites are complete
4. Verification steps will effectively confirm the fix
5. Edge cases and potential issues are addressed
Provide specific feedback for improvements.""",
            gemini_api_key=gemini_api_key,
            model=model
        )
        
        formatter = GeminiAgent(
            name="Formatter",
            system_message="""You are a document formatting specialist who ensures runbooks are properly structured and formatted.
Your task is to take the finalized runbook content and ensure:
1. The markdown formatting is consistent and professional
2. Headers are properly nested and follow a logical structure
3. Code blocks, tables, and lists are properly formatted
4. The document has a professional appearance and is easy to read
5. The final document is ready for distribution to IT staff
Provide the final formatted runbook in pristine markdown format.""",
            gemini_api_key=gemini_api_key,
            model=model
        )
        
        # Step 2: Execute the workflow sequentially (avoid using GroupChat)
        print("Step 1: Analyst is analyzing the issue...")
        analyst_response = user_proxy.initiate_chat(
            analyst,
            message=f"Please analyze this issue thoroughly:\n\n{issue_description}\n\nProvide a detailed analysis."
        )
        
        print("Step 2: RunbookWriter is creating a draft...")
        runbook_draft = user_proxy.initiate_chat(
            runbook_writer,
            message=f"""Based on the analyst's analysis and the original issue, create a comprehensive runbook.
            
Original issue:
{issue_description}

Analysis:
{analyst_response}

Please create a detailed runbook in markdown format.
"""
        )
        
        print("Step 3: TechnicalReviewer is reviewing the draft...")
        review_feedback = user_proxy.initiate_chat(
            reviewer,
            message=f"""Please review this runbook draft:

{runbook_draft}

Provide specific feedback for technical improvements.
"""
        )
        
        print("Step 4: Formatter is finalizing the document...")
        final_runbook = user_proxy.initiate_chat(
            formatter,
            message=f"""Please format this runbook into a clean, professional document:

Runbook draft:
{runbook_draft}

Technical review feedback:
{review_feedback}

Create the final polished runbook in clean markdown format.
"""
        )
        
    except Exception as e:
        print(f"Error in AutoGen workflow: {str(e)}")
        print("Falling back to direct generation...")
        final_runbook = generate_direct_with_gemini(issue_description, model, gemini_api_key)
    
    # Save the final runbook to a file
    with open(output_file, "w") as f:
        f.write(final_runbook)
    
    print(f"Runbook created and saved to '{output_file}'")
    return output_file

def generate_direct_with_gemini(issue_description, model="gemini-1.5-pro", api_key=None):
    """Fallback function to generate runbook directly with Gemini."""
    try:
        # Set up the API key if provided
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key
            
        # Initialize the Google Generative AI library
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # Configure the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Create the model instance
        model_instance = genai.GenerativeModel(model_name=model, generation_config=generation_config)
        
        # Create a comprehensive prompt
        prompt = f"""
Create a comprehensive runbook for the following issue:

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
        response = model_instance.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Fallback also failed: {str(e)}")
        return f"# Error Generating Runbook\n\nFailed to generate runbook: {str(e)}"

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
        # Create the runbook using AutoGen with Gemini
        output_file = create_runbook_from_steps(
            issue_description=example_issue,
            output_file="server_crash_runbook.md",
            gemini_api_key="AIzaSyCqNI95axOXHF53c4SDtElyZ75F__mMKwY",  # Your API key
            model="gemini-1.5-pro"  # Can also use "gemini-1.5-flash" for faster responses
        )
        print(f"Runbook created successfully at: {output_file}")
        
        # Display the contents of the created file
        with open(output_file, 'r') as f:
            print("\nRunbook contents:")
            print(f.read())
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")