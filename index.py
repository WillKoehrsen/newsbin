from flask import Flask, request, render_template
from engine import filters
app = Flask(__name__)

@app.route("/")
@app.route("/<source>")
def index( source ):
    sources = filters.all()
    return render_template('index.html', sources=sources)

if __name__ == "__main__":
    app.run()
