from flask import Flask, jsonify, render_template
import wordsgenerator

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<word>")
def json_word_from_url(word):
    return render_template("answer.html", data=wordsgenerator.get_words(word))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)