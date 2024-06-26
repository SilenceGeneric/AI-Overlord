import os
import openai
import subprocess
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_env_var(var_name):
    """Get an environment variable and log an error if not found."""
    value = os.getenv(var_name)
    if value is None:
        logger.error(f"Environment variable {var_name} not found.")
        raise ValueError(f"{var_name} not found. Please set the {var_name} environment variable.")
    return value

# Load environment variables securely
openai_api_key = get_env_var("OPENAI_API_KEY")
other_ai_api_url = get_env_var("OTHER_AI_API_URL")
other_ai_api_key = get_env_var("OTHER_AI_API_KEY")

openai.api_key = openai_api_key

def get_openai_response(prompt, model="text-davinci-003"):
    """Get a response from OpenAI's API."""
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=150,
            temperature=0.5,
            stop=["\n\n"],
        )
        return response.choices[0].text.strip()
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        return f"OpenAI API error: {e}"

def execute_command(command):
    """Execute a shell command and return its output."""
    try:
        logger.info("Executing shell command")
        result = subprocess.run(command.split(), capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command error: {e.output}")
        return f"Command error: {e.output}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Unexpected error: {str(e)}"

def interact_with_other_ai(api_url, api_key, prompt):
    """Interact with another AI tool using a provided API."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"prompt": prompt, "max_tokens": 150}
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("text", "").strip()
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return f"Request error: {e}"
    except (KeyError, IndexError) as e:
        logger.error(f"Response parsing error: {e}")
        return f"Response parsing error: {e}"

def orchestrate_task(prompt):
    """Determine the type of task based on the user's prompt and handle accordingly."""
    task_decision_prompt = f"Determine if the following prompt should be handled as a shell command, code generation, or by another AI tool: {prompt}"
    decision = get_openai_response(task_decision_prompt)

    if "Shell Command:" in decision:
        command = decision.split("Shell Command:")[1].strip()
        return execute_command(command)

    elif "Code Generation:" in decision:
        code_prompt = decision.split("Code Generation:")[1].strip()
        return get_openai_response(code_prompt, model="code-davinci-002")

    elif "AI Tool:" in decision:
        instruction = decision.split("AI Tool:")[1].strip()
        return interact_with_other_ai(other_ai_api_url, other_ai_api_key, instruction)

    else:
        logger.error("Error: Unable to determine task type from decision.")
        return "Error: Unable to determine task type from decision."

def main():
    """Main function to interact with the user and process their prompts."""
    print("Welcome to the Advanced AI-Powered Coding System!")
    print("Enter your coding prompt (or 'exit' to quit):")
    while True:
        user_prompt = input("You: ")
        if user_prompt.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        result = orchestrate_task(user_prompt)
        print(f"Result: {result}")

if __name__ == "__main__":
    main()
