import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import Text
import threading
import ollama
import os
import subprocess

# Set dark theme colors
text_bg = "#262424"
text_fg = "#fafafa"
dark_bg = "#171717"  # Dark gray background
light_fg = "#D9D9D9"  # Light gray text
input_bg = "#252526"  # Slightly lighter gray for input field
button_bg = "#2D2D2D"  # Button background
button_fg = "#FFFFFF"  # White text for buttons

# Global variable to control the stream
stream_control = {"active": True}

language_models = ['llama2', 'mistral', 'llama2:13b', 'llama2-uncensored', 'llava', 'codellama:34b',
                   'deepseek-coder:33b', 'sqlcoder']

# Function to handle the interaction with ollama
def ask_ollama(question, text_widget, stream_control, model_name):
    stream_control["active"] = True  # Start streaming
    stream = ollama.chat(
        model=model_name,
        messages=[{'role': 'user', 'content': question}],
        stream=True,
    )

    text_widget.configure(state='normal')  # Enable editing of the widget
    text_widget.delete('1.0', tk.END)  # Clear the current content

    for chunk in stream:
        if not stream_control["active"]:  # Stop streaming if control is set to False
            break
        text_widget.insert(tk.END, chunk['message']['content'])
        text_widget.see(tk.END)  # Auto-scroll as text is inserted
        text_widget.update_idletasks()  # Update the widget

    text_widget.configure(state='disabled')  # Disable editing of the widget


# Update the submit_question
def submit_question():
    question = question_text.get("1.0", tk.END).strip()  # Get text from Text widget
    selected_model = model_selector.get()  # Get the selected model from the Combobox
    if question:  # Check if the question is empty
        threading.Thread(target=ask_ollama, args=(question, response_text, stream_control, selected_model)).start()


# Function to clear the question and answer
def clear_text():
    question_entry.delete(0, tk.END)
    response_text.configure(state='normal')
    response_text.delete('1.0', tk.END)
    response_text.configure(state='disabled')


# Function to stop the ollama response stream
def stop_stream():
    stream_control["active"] = False  # Set the stream control to False to stop the stream


# Function to save the conversation to an MD file and open it
def save_and_open_md():
    content = response_text.get("1.0", tk.END)
    filename = "ollama_conversation.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    # Open the MD file in the default markdown editor
    if os.name == 'posix':  # If the system is macOS or Linux
        subprocess.call(('open', filename))
    elif os.name == 'nt':  # If the system is Windows
        os.startfile(filename)
    else:  # Fallback for other OS
        subprocess.call(('xdg-open', filename))


# Create the main window
root = tk.Tk()
root.title("Ollama Chat")
root.configure(bg=dark_bg)

# Adjust layout for dynamic resizing
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)  # Response text grows

# Create a Frame for the question entry and submit button
entry_frame = tk.Frame(root, bg=dark_bg)
entry_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
entry_frame.columnconfigure(0, weight=1)

# Create the question entry widget
question_entry = tk.Entry(entry_frame, bg=text_bg, fg=text_fg, insertbackground=text_fg)
question_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
# question_entry.bind("<Return>")

# Create the question Text widget instead of Entry
question_text = Text(entry_frame, height=1, bg=text_bg, fg=text_fg, insertbackground=text_fg, wrap='word')
question_text.grid(row=0, column=0, sticky='ew', padx=(0, 10))

def adjust_text_height(event=None):
    # Calculate the number of lines in the Text widget
    lines = int(question_text.index('end-1c').split('.')[0])
    question_text.config(height=lines)  # Adjust the height based on the number of lines

# Bind this function to Text widget's changes
question_text.bind('<KeyPress>', adjust_text_height)
question_text.bind('<KeyRelease>', adjust_text_height)

# Create the model selector Combobox
model_selector = ttk.Combobox(entry_frame, values=language_models, state='readonly', width=15)
model_selector.grid(row=0, column=1, padx=10)
model_selector.set('llama2')  # Set the default value

# Create the submit button
submit_button = tk.Button(entry_frame, text="Ask model", command=submit_question, bg=button_bg, fg=button_fg)
submit_button.grid(row=0, column=2, padx=10)

# Create the response Text widget
response_text = scrolledtext.ScrolledText(root, bg=text_bg, fg=text_fg, insertbackground=text_fg, state='disabled', wrap=tk.WORD)
response_text.grid(row=1, column=0, sticky='nsew', pady=(10, 0))

# # Create the submit button
# submit_button = tk.Button(entry_frame, text="Ask Ollama", command=submit_question, bg=button_bg, fg=button_fg)
# submit_button.grid(row=0, column=1)

# Create the response Text widget
response_text = scrolledtext.ScrolledText(root, bg=text_bg, fg=text_fg, insertbackground=text_fg, state='disabled',wrap=tk.WORD)
response_text.grid(row=1, sticky='nsew', pady=(10, 0))

# Create the delete button
delete_button = tk.Button(root, text="Delete", command=clear_text, bg=button_bg, fg=button_fg)
delete_button.grid(row=2, column=0, sticky='we', padx=10, pady=10)

# Create the stop button
stop_button = tk.Button(root, text="Stop", command=stop_stream, bg=button_bg, fg=button_fg)
stop_button.grid(row=3, column=0, sticky='ew', padx=10, pady=10)

# Create the save button
save_button = tk.Button(root, text="Save", command=save_and_open_md, bg=button_bg, fg=button_fg)
save_button.grid(row=4, column=0, sticky='we', padx=10, pady=10)

# Start the GUI event loop
root.mainloop()