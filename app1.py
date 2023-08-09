from flask import Flask, request, render_template_string
from german_flash_card_def_function import generate_flash_cards

app = Flask(__name__)

# HTML template for the input form
HTML_TEMPLATE = """
<!doctype html>
<html>
    <head><title>German to English Flash Card Generator</title></head>
    <body>
        <h1>Enter German Text</h1>
        <form action="/generate" method="post">
            <textarea name="german_text" rows="5" cols="40"></textarea><br>
            <input type="submit" value="Generate Flash Cards">
        </form>
        <pre>{{ flash_cards }}</pre>
    </body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)  # Render the input form

@app.route('/generate', methods=['POST'])
def generate():
    german_text = request.form['german_text']  # Get the German text from the form
    flash_cards = generate_flash_cards(german_text)  # Generate the flash cards using your function
    return render_template_string(HTML_TEMPLATE, flash_cards=flash_cards)  # Render the flash cards

if __name__ == '__main__':
    app.run(debug=True)
