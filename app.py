
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>Tsukuyomi: Letters for the Unknown</h1><p>Our journey begins beneath the moon.</p>"


if __name__ == "__main__":
    app.run(debug=True)
