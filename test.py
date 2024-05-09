from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def index():
    # Redirect to google.com
    return redirect("https://www.google.com")

if __name__ == '__main__':
    app.run(debug=True)