import os
import autogen
import google.generativeai as genai

class GeminiAgent(autogen.ConversableAgent):
    """Simple agent that uses Gemini API"""
    
    def __init__(self, name, system_message, api_key=None, model="gemini-1.5-pro"):
        super().__init__(name=name, system_message=system_message)
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=model)
    
    def generate_reply(self, messages, sender, **kwargs):
        # Simple prompt construction
        prompt = f"System: {self.system_message}\n\n"
        prompt += f"User: {messages[-1]['content']}\n\n"
        prompt += "Assistant: "
        
        # Generate with Gemini
        response = self.model.generate_content(prompt)
        return response.text

def create_runbook(issue_description, output_file="runbook.md", api_key=None):
    """Simplified runbook creation with a single agent"""
    
    # Create agent
    runbook_writer = GeminiAgent(
        name="RunbookWriter",
        system_message="""Create a comprehensive runbook for technical issues including:
1. Title and executive summary
2. Description and impact
3. Prerequisites
4. Implementation steps
5. Verification steps
6. Rollback instructions
7. Troubleshooting
Format in markdown.""",
        api_key=api_key
    )
    
    # User proxy
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=0,
        code_execution_config={
        "work_dir": ".",
        "use_docker": False  # Explicitly disable Docker
        }
    )
    
    # Single interaction
    response = user_proxy.initiate_chat(
        runbook_writer,
        message=f"Create a runbook for this issue:\n\n{issue_description}"
    )
    
    # Save output
    with open(output_file, "w") as f:
        f.write(response)
    
    return output_file

# Example usage
if __name__ == "__main__":
    # Use a shorter issue description to reduce token usage
    issue = """
    Issue: Application server crashes under high load
    Description: Server crashes at 500+ users with Out of Memory errors
    Fix Steps:
    1. Increase JVM heap to 4GB
    2. Set connection limit to 400
    3. Fix memory leak in UserSessionManager.java
    4. Add memory monitoring
    5. Set up load balancing
    """
    
    output_file = create_runbook(
        issue_description=issue,
        api_key="AIzaSyCqNI95axOXHF53c4SDtElyZ75F__mMKwY"  # Replace with your key
    )
    print(f"Runbook saved to {output_file}")