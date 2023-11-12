# export FLASK_APP=app_L5
import os
import json
import openai
import utils_L5 # Helper-Functions zur besseren Übersichtlichkeit nach 'utils_L5.py' ausgelagert 
from flask import Flask, redirect, render_template, request, url_for
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

app = Flask(__name__)
openai.api_key  = os.environ['OPENAI_API_KEY']

@app.route("/", methods=("GET", "POST"))
def index():
    # Wenn der Nutzer seine Frage eingibt und mit der Eingabeaste ("ENTER") abschließt
    # löst er den Aufruf über die POST-Funktion aus. Die User-Eingabe wird ausgelesen,
    # über GPT ein Antworttext erzeugt und über den REDIRECT Befehl eine GET-Funktion erzeugt
    if request.method == "POST":
        user_prompt = request.form["user_prompt"]
        messages = generate_prompt(user_prompt)
        result, token_count = utils_L5.get_completion_from_messages(messages)
        return redirect(url_for("index", result=result, token_count=token_count))

    # Falls der Aufruf über die GET-Funktion erfolgt, werden die Argumente result und token_count
    # aus der URL ausgelesen und die HTML-Seite index_L5.html erstellt ("gerendert")
    result = request.args.get("result")
    token_count = request.args.get("token_count")
    return render_template("index_L5.html", result=result, token_count=token_count)


def generate_prompt(user_prompt):
# Ergänzt die Nutzerfrage mit Anweisungen für die System-Rolle sowie Katalog- und Produktinformationen für die
# Assistenten-Rolle und erzeugt daraus eine 'List of Dictionaries' als Input für einen nachfolgenden GPT Aufruf
# Die Katalog- und Produktinformation wird aufwändig & mehrstufig auf Basis des User-Prompts aus dem Prouktkatalog extrahiert
    system_message = f"""
    You are a customer service assistant for a \
    large electronic store. \
    Respond in a friendly and helpful tone. \
    Make sure to ask the user relevant follow up questions.
    """
    product_information_for_user = product_information_for_user_message(user_prompt)

    messages =  [
    {'role':'system',
     'content': system_message},
    {'role':'user',
     'content': user_prompt},
    {'role':'assistant',
     'content': f"""Relevant product information:\n\
     {product_information_for_user}"""},
    ]
    return messages

def product_information_for_user_message(user_prompt):
# Bei grossen Produktkatalogen können nicht bei jeder User-Abfrage alle Produktinformationen
# als System-Message mitgliefert werden; diese Funktion erstellt auf Basis des User-Prompts
# einen "Sub-Katalog" nur mit den Katalog- und Produktnamen sowie Produktinformationen, die im User-Prompt erwähnt sind

    category_and_product = utils_L5.category_and_product_response(user_prompt)
    # Nutzt GPT um aus dem User-Prompt zunächste nur die Produkte und Kategorien zu extrahieren
    # Output a python list of objects, where each object has the following format:
    #        'category': <one of Computers and Laptops, \
    #        Smartphones and Accessories, \
    #        Televisions and Home Theater Systems, \
    #        Gaming Consoles and Accessories,
    #        Audio Equipment, Cameras and Camcorders>,
    #    OR
    #        'products': <a list of products that must \
    #        be found in the allowed products below>

    category_and_product_list = utils_L5.read_string_to_list(category_and_product)
    # Die Python-Funktion 'read_string_to_list' nimmt einen String (input_string)
    # als Eingabe und versucht, diesen String in ein JSON-Format zu konvertieren
    # und als Python-Liste oder -Dictionary zurückzugeben.

    product_information_string = utils_L5.generate_output_string(category_and_product_list)
    # Wenn das Schlüsselwort "category" enthalten ist, durchsucht die Funktion das products-Dictionary
    # nach Produkten in dieser Kategorie und fügt sie zum output_string hinzu.
    # Wenn das Schlüsselwort "products" enthalten ist, durchsucht die Funktion
    # das products-Dictionary nach diesen Produkten, und fügt die Produktdaten zum output_string hinzu.

    return product_information_string
