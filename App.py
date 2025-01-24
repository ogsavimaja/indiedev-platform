from flask import Flask, render_template

app = Flask(__name__)

# Pass the required route to the decorator
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)