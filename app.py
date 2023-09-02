import os
import openai
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
import schedule
import threading
import time
import speech_recognition as sr
import socket

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize tasks with tasks loaded from the file
tasks = []

# Replace with OpenAI API key
openai.api_key = "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"

# Create a socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def recognize_audio_from_microphone(language="en-US"):
    try:
        prompt = "Please transcribe the following audio:"

        response = openai.Completion.create(
            engine="whisper",
            prompt=prompt,
            max_tokens=100,
            temperature=0,
            top_p=1.0,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
        )

        transcription = response.choices[0].text.strip()
        return transcription
    except openai.error.OpenAIError as e:
        error_message = "An error occurred while processing your request. Please try again later."
        flash(error_message, "error")
        return None

def send_reminder(task, time):
    print(f"Reminder for task: {task} at {time}")
    flash(f"Reminder: '{task}' at {time}")

def schedule_reminders():
    reminders = [("Task 1", "09:00 AM"), ("Task 2", "12:30 PM"), ("Task 3", "04:15 PM")]
    for reminder in reminders:
        task, time = reminder
        schedule.every().day.at(time).do(send_reminder, task=task, time=time)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

def save_tasks_to_file(tasks):
    with open('tasks.txt', 'w') as file:
        for task, completed in tasks:
            file.write(f"{task},{completed}\n")

def load_tasks_from_file():
    tasks = []
    try:
        with open('tasks.txt', 'r') as file:
            for line in file:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    task, completed = parts
                    tasks.append((task, completed == 'True'))
    except FileNotFoundError:
        pass  # Ignore if the file does not exist
    return tasks

# Load tasks from the file when the application starts
tasks = load_tasks_from_file()

@app.route('/')
def index():
    enumerated_tasks = enumerate(tasks)  # Enumerate the tasks here
    return render_template('index.html', tasks=enumerated_tasks)

@app.route('/start-recording', methods=['GET', 'POST'])
def start_recording():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Say something...")
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        print("Sorry, I could not understand what you said.")
        return jsonify({"text": "Unknown value error"})
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return jsonify({"text": "Request error"})

@app.route('/record-and-transcribe', methods=['GET', 'POST'])
def record_and_transcribe():
    if request.method == 'POST':
        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                print("Say something...")
                audio = recognizer.listen(source)

            transcribed_text = recognizer.recognize_google(audio)
            return render_template('transcribe.html', transcribed_text=transcribed_text)

        except sr.UnknownValueError:
            error_message = "Sorry, I could not understand what you said."
            flash(error_message, "error")
        except sr.RequestError as e:
            error_message = f"Could not request results from Google Speech Recognition service; {str(e)}"
            flash(error_message, "error")

    return render_template('record.html')

@app.route('/add-task', methods=['POST'])
def add_task():
    task = request.form.get('task')
    if task:
        tasks.append((task, False))  # Initialize new tasks as not completed
        save_tasks_to_file(tasks)  # Save tasks to the file
    return redirect(url_for('index'))

@app.route('/complete-task/<int:task_index>')
def complete_task(task_index):
    if 0 <= task_index < len(tasks):
        task, completed = tasks[task_index]
        tasks[task_index] = (task, not completed)  # Toggle completion status
        save_tasks_to_file(tasks)  # Save updated tasks to the file
    return redirect(url_for('index'))

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    app.run(debug=True)

    # Close the socket when the application exits
    s.close()
