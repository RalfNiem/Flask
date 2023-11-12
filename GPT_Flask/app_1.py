# export FLASK_APP=app_1
import os
import openai
import tiktoken
from flask import Flask, render_template, request
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

app = Flask(__name__)
GPT_MODEL = "gpt-3.5-turbo"
encoding = tiktoken.encoding_for_model(GPT_MODEL)
MAX_TOKEN = 100

# in dieser Version wird jede neue User Frage/Input an den bisherigen Chat-Verlauf drangehängt,
# um so einen Chat-Context zu schaffen und für die Antwort den gesamten Chat-Verlauf in Betracht zu ziehen
messages =  [{'role':'system', 'content':"You are an assistant who always responds to user questions in german"}]

@app.route('/')
def index():
    return render_template('index.html', result='', token_count='')

@app.route('/submit', methods=['POST'])
def submit():
    input_text = request.form['input_text']
    print(GPT_MODEL)
    messages.append({'role':'user','content': input_text})
    messages = limit_message_length(messages, MAX_TOKEN)
    response = openai.ChatCompletion.create(
        model= GPT_MODEL,
        messages=messages,
        temperature=0.4,
    )
    result = response.choices[0].message["content"]
    token_count = response['usage']['total_tokens']
    return render_template('index.html', result=result, token_count=token_count)

def limit_message_length(messages, max_token = 100):
    num_tokens = len(encoding.encode(messages))
    print(f"Aktuelle Länges des Promts in [Token]: {num_tokens}")
    return messages

if __name__ == '__main__':
    app.run()
