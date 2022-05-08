from crypt import methods
from flask import Flask, jsonify, redirect, render_template, request, url_for
import wordsgenerator

app = Flask(__name__)
russ_dict = wordsgenerator.make_russian_dict()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["GET", "POST"])
def result_from_url():
    if request.method == 'POST':
        params = {key: val for key, val in request.form.items()}

        return render_template(
            "answer.html",
            data=wordsgenerator.get_words(
                **params,
                russ_dict=russ_dict,
            ).dict(),
        )
    else:
        return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
