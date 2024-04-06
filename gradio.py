import gradio as gr
import ollama
import os
import json
import datetime

# Global variable to control the stream
stream_control = {"active": True}

# List of available language models
language_models = ['llama2', 'mistral', 'llama2:13b', 'llama2-uncensored', 'llava', 'codellama:34b',
                   'deepseek-coder:33b', 'sqlcoder']

chat_history = []


def load_chat_history():
    global chat_history
    try:
        with open('chat_history.json', 'r') as f:
            chat_history = json.load(f)
    except FileNotFoundError:
        chat_history = []


def save_chat_history():
    folder_name = 'chat_history'
    history_chat_file = os.path.join(folder_name, 'chat_history.json')
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    existing_data = []
    if os.path.isfile(history_chat_file) and os.path.getsize(history_chat_file) > 0:
        with open(history_chat_file, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.extend(chat_history)
    with open(history_chat_file, 'w') as f:
        json.dump(existing_data, f)
    print("Chat history saved successfully.")


def clear_history():
    global chat_history
    chat_history = []  # Reset the in-memory chat history

    # Specify the path to the chat history file
    # folder_name_1 = 'Ollama'  # Ensure this folder exists
    # folder_name_2 = 'chat_history'  # Ensure this folder exists
    # history_chat_file = os.path.join(folder_name_1, folder_name_2, 'chat_history.json')
    history_chat_file = r'C:\Users\szyme\PycharmProjects\Stock_analyzer\Ollama\chat_history\chat_history.json'

    # Clear the contents of the file
    if os.path.exists(history_chat_file):
        with open(history_chat_file, 'w') as f:
            json.dump(chat_history, f)  # Write an empty list to the file
        print("Chat history cleared successfully.")


def ask_ollama(question, model_name):
    global chat_history
    stream_control["active"] = True

    timestamp = datetime.datetime.now().isoformat()

    if question.strip():
        chat_history.append({'role': 'user', 'content': question, 'timestamp': timestamp})
    else:
        print("Empty question detected, not appending to history.")
        return "Please enter a question."

    sanitized_history = [msg for msg in chat_history if msg.get('content').strip()]

    response_content = ""

    try:
        stream = ollama.chat(
            model=model_name,
            messages=sanitized_history,
            stream=True,
        )

        for chunk in stream:
            if not stream_control["active"]:
                break
            response_content += chunk['message']['content']

        if response_content.strip():
            chat_history.append({'role': 'system', 'content': response_content})

    except Exception as e:
        print(f"Error during chat: {e}")
        return f"Error: {e}"

    return response_content


def process_chat_history_upload(file_content):
    global chat_history
    if file_content is not None:
        content = file_content["content"]
        chat_history = json.loads(content.decode("utf-8"))
        print("Chat history loaded from uploaded file.")
    else:
        print("No file uploaded.")


def app(question, model_name, action):
    if action:
        if action == "Clear Chat":
            clear_history()
            return "Chat history cleared."
        elif action == "Save Chat":
            save_chat_history()
            return "Chat history saved."
        elif action == "Load Chat":
            load_chat_history()
            return "Chat history loaded."
    else:
        return ask_ollama(question, model_name)


# Create Gradio Interface
question_input = gr.Textbox(lines=2, placeholder="Enter your question here...")
model_selector = gr.Dropdown(choices=language_models, label="Model")
action_menu = gr.Dropdown(choices=["", "Clear Chat", "Save Chat", "Load Chat"], label="Action")
chat_history_display = gr.State(chat_history)  # Use State to manage and display chat history

file_upload = gr.File(label="Upload Chat History", type="file")


def update_interface(question, model_name, action, file_content=None):
    global chat_history  # Ensure you have access to the global variable

    if action == "Load Chat":
        process_chat_history_upload(file_content)
        # Since chat history is a global variable, ensure any display components are updated accordingly
    elif action == "Clear Chat":
        clear_history()  # This now also clears the 'chat_history.json' file
        print("Chat history cleared.")
    elif action == "Save Chat":
        save_chat_history()
        print("Chat history saved.")
    else:  # Default action is to process the question
        return ask_ollama(question, model_name)

    # This part depends on how you wish to handle/display the result
    # For simplicity, we're returning a placeholder string
    return "Operation completed."


# Setup Gradio interface with the new file upload component
interface = gr.Interface(
    fn=update_interface,
    inputs=[question_input, model_selector, action_menu, file_upload],
    outputs="text",
    title="Ollama Chat",
    description="Ask a question to the model or manage chat history."
)

interface.launch()

# def app(question, model_name, action):
#     if action:
#         if action == "Clear Chat":
#             clear_history()
#             return "Chat history cleared.", ""  # Return an empty string for the chat history display
#         elif action == "Save Chat":
#             save_chat_history()
#             return "Chat history saved.", ""  # Optionally, return the current chat history as a string
#         elif action == "Load Chat":
#             load_chat_history()
#             # Convert the chat history to a string and return it
#             chat_history_str = "\n".join([f"{entry['role']}: {entry['content']}" for entry in chat_history])
#             return "Chat history loaded.", chat_history_str
#     else:
#         response = ask_ollama(question, model_name)
#         # Optionally, append the response to the chat history and return it as a string
#         return response, ""  # Adjust this part based on how you want to display the response
#
#
# # Create Gradio Interface with a Textbox for displaying the chat history
# question_input = gr.Textbox(lines=2, placeholder="Enter your question here...")
# model_selector = gr.Dropdown(choices=language_models, label="Model")
# action_menu = gr.Dropdown(choices=["", "Clear Chat", "Save Chat", "Load Chat"], label="Action")
# chat_history_display = gr.Textbox(lines=10, label="Chat History")  # Use a Textbox for displaying the chat history
#
# submit_button = gr.Interface(fn=app, inputs=[question_input, model_selector, action_menu],
#                              outputs=[gr.Textbox()],
#                              title="Ollama Chat",
#                              description="Ask a question to the model.")
#
# submit_button.launch()
