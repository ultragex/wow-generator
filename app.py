from flask import Flask, render_template, request, redirect, url_for
from glossary import Words

app = Flask(__name__)
# russ_dict = wordsgenerator.make_russian_dict()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["GET", "POST"])
def result_from_url():
    if request.method == "POST":
        params = {key: val for key, val in request.form.items()}

        try:
            words = Words(
                symbols=request.form["sample"],
                minimum=int(request.form["result_min"]),
                maximum=int(request.form["result_max"]),
            ).get_words()
            response = {
                "success": bool(words),
                "words": words if words else None,
                "request": params,
                "message": None if words else "Ничего не получилось",
            }
        except Exception as exc:
            response = {
                "success": False,
                "request": params,
                "message": exc,
            }

        return render_template(
            "answer.html",
            data=response,
        )
    else:
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
