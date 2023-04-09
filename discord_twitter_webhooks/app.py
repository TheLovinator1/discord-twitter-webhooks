from typing import Literal

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world() -> Literal["<p>Hello, World!</p>"]:
    return "<p>Hello, World!</p>"
