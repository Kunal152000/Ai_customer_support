import smtplib
import os
from email.message import EmailMessage

class EmailService:
    def __init__(self):
        self.gmail_user = os.getenv("GMAIL")
        self.gmail_password = os.getenv("GOOGLE_APP_PASSWORD")

    def send_otp(self, to_email: str, otp: str):
        if not self.gmail_user or not self.gmail_password:
            print("WARNING: Email credentials not configured in .env file.")
            return

        msg = EmailMessage()
        msg['Subject'] = 'Your Password Reset OTP'
        msg['From'] = self.gmail_user
        msg['To'] = to_email

        html_content = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello,</p>
                <p>We received a request to reset your password. Here is your One-Time Password (OTP):</p>
                <div style="background-color: #f4f4f4; padding: 15px; text-align: center; border-radius: 5px; margin: 20px 0;">
                    <h1 style="color: #4A90E2; letter-spacing: 5px; margin: 0;">{otp}</h1>
                </div>
                <p>This OTP will safely expire in <strong>7 minutes</strong>.</p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </body>
        </html>
        """
        msg.set_content(f"Your password reset OTP is {otp}. It expires in 7 minutes.") 
        msg.add_alternative(html_content, subtype='html')

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.gmail_user, self.gmail_password)
                smtp.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
