from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/submit", methods=["POST"])
def submit():
    email = request.form.get("email")
    message = request.form.get("message")
    app.logger.info(f"Email: {email}")
    app.logger.info(f"Message: {message}")
    print(email)
    return f"Form submitted with email: {email} and message: {message}"

if __name__ == "__main__":
    app.run(debug=True)
