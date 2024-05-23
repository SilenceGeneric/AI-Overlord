import os
import openai
import subprocess
import requests

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_response(prompt, model = "text-davinci-003"):
response = openai.Completion.create(
    engine = model,
    prompt = prompt,
    max_tokens = 150,
    temperature = 0.5,
    stop = ["\n\n"]
)
return response.choices[0].text.strip()


def execute_command(command):
try:
result = subprocess.check_output(
    command,
    shell = True,
    stderr = subprocess.STDOUT,
    universal_newlines = True
)
except subprocess.CalledProcessError as e:
result = e.output
return result


def interact_with_other_ai(api_url, api_key, prompt):
headers = {
    'Authorization': f'Bearer {
        api_key
    }',
    'Content-Type': 'application/json'
}
data = {
    'prompt': prompt,
    'max_tokens': 150
}
response = requests.post(api_url, headers = headers, json = data)
if response.status_code == 200:
return response.json()['choices'][0]['text'].strip()
else :
return f"Error: {
    response.status_code
} - {
    response.text
}"


def orchestrate_task(prompt):
# Determine the task based on the user's input
task_decision_prompt = f"Determine if the following prompt should be handled as a shell command, code generation, or by another AI tool: {
    prompt
}"
decision = get_openai_response(task_decision_prompt)

if "Shell Command:" in decision:
command = decision.split("Shell Command:")[1].strip()
print(f"Executing command: {
    command
}")
output = execute_command(command)
return output

elif "Code Generation:" in decision:
code_prompt = decision.split("Code Generation:")[1].strip()
generated_code = get_openai_response(code_prompt, model = "code-davinci-002")
return generated_code

elif "AI Tool:" in decision:
instruction = decision.split("AI Tool:")[1].strip()
other_ai_api_url = "YOUR_OTHER_AI_API_URL" # Replace with actual API URL
other_ai_api_key = "YOUR_OTHER_AI_API_KEY" # Replace with actual API key
other_ai_response = interact_with_other_ai(other_ai_api_url, other_ai_api_key, instruction)
return other_ai_response

else :
return "Error: Unable to determine task type from decision."


def main():
print("Welcome to the Advanced AI-Powered Coding System!")
print("Enter your coding prompt (or 'exit' to quit):")
while True:
user_prompt = input("You: ")
if user_prompt.lower() in ['exit', 'quit']:
print("Exiting...")
break
result = orchestrate_task(user_prompt)
print(result)


if __name__ == "__main__":
main()