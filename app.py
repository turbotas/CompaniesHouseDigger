from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"

if __name__ == "__main__":
    # For local dev only; use a production WSGI server in production
    app.run(debug=True)
