# export FLASK_APP=app
import os
import openai
from flask import Flask, render_template, request
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', result='', token_count='')

@app.route('/submit', methods=['POST'])
def submit():
    input_text = request.form['input_text']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=generate_prompt(input_text),
        temperature=0.6,
    )
    result = response.choices[0].message["content"]
    token_count = response['usage']['total_tokens']
    return render_template('index.html', result=result, token_count=token_count)


def generate_prompt(prompt):
    messages =  [
    {'role':'system',
    'content':"""You are an assistant who always responds to user questions in german"""},
    {'role':'user', 'content': prompt}
    ]
    return messages


if __name__ == '__main__':
    app.run()
