from flask import Flask, render_template, request, session
import secrets
import time
import smtplib

app = Flask(__name__)
app.secret_key = "supersecretkey"   # required for session


# 🔐 Generate OTP
def generate_otp():
    return ''.join(str(secrets.randbelow(10)) for _ in range(6))


# 📧 Send Email
def send_email(receiver_email, otp):
    sender_email = "vanshtanwar995@gmail.com"
    app_password = "kllvlyxqzjcamiep"

    message = f"Subject: OTP Verification\n\nYour OTP is: {otp}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    expiry = session.get("expiry", 0)

    if request.method == "POST":
        action = request.form.get("action")

        # 🔹 Generate OTP
        if action == "generate":
            email = request.form.get("email")

            otp = generate_otp()
            session["otp"] = otp
            session["expiry"] = time.time() + 300
            session["attempts"] = 3

            send_email(email, otp)

            message = "✅ OTP sent to your email!"

        # 🔹 Verify OTP
        elif action == "verify":
            user_otp = request.form.get("OTP")

            if time.time() > session.get("expiry", 0):
                message = "❌ OTP expired!"

            elif user_otp == session.get("otp"):
                message = "✅ Verified successfully!"

            else:
                attempts = session.get("attempts", 0) - 1
                session["attempts"] = attempts

                if attempts > 0:
                    message = f"❌ Wrong OTP! Attempts left: {attempts}"
                else:
                    message = "🚫 Too many attempts!"

    return render_template("index.html", message=message, expiry=expiry)


if __name__ == "__main__":
    app.run(debug=True)