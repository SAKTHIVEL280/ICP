from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Internal Complaint Portal Backend is Running!"
@app.route("/health")
def health():
    return "Health Check Passed"
if __name__ == "__main__":
    app.run(debug=True)