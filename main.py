import pandas as pd
import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# -------- Load ENV --------
load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

CSV_FILE = "hr_contacts.csv"
RESUME_PATH = "Manvendra_Rajpoot_Resume.pdf"


# -------- Email Content --------
def generate_email(row):
    name = str(row.get("Name", "")).strip()
    email = str(row.get("Email", "")).lower()
    company = str(row.get("Company", "")).strip() or "your company"

    greeting = f"Hi {name}," if name and len(name) < 25 else "Hello,"

    redirect_line = ""
    if "hr@" in email or "careers@" in email:
        redirect_line = "\nIf there's someone appropriate to connect with regarding backend roles, I’d appreciate being pointed in the right direction.\n"

    return f"""
{greeting}

I’m reaching out regarding backend opportunities at {company}.

I’m currently working as a Backend Developer, building AI-powered systems, multi-tenant SaaS architectures, and secure APIs using Django and FastAPI.

Some of my recent work includes:
- AI-driven systems improving response quality
- Multi-tenant SaaS platforms with secure access
- Real-time notification systems
- Scalable background job processing

I also have experience with Docker, Kubernetes, CI/CD, and database optimization.
{redirect_line}
I’ve attached my resume for your review.

Best regards,
Manvendra Rajpoot
"""


# -------- Build Email Message --------
def build_message(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    # Attach resume
    with open(RESUME_PATH, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment; filename=Manvendra_Rajpoot_Resume.pdf",
    )

    msg.attach(part)

    return msg


# -------- Main --------
def main():
    # Load CSV
    df = pd.read_csv(CSV_FILE)

    # Clean data
    df = df.dropna(subset=["Email"])
    df["Email"] = df["Email"].str.strip().str.lower()
    df = df.drop_duplicates(subset=["Email"])

    print(f"Total emails after cleaning: {len(df)}")

    # Open ONE SMTP connection
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)

        for index, row in df.iterrows():
            email = row["Email"]
            company = str(row.get("Company", "")).strip()

            # subject = f"Backend Developer (Django | AI Systems | SaaS) – {company}"
            subject = f"Application: Backend, AI Systems & SaaS Engineering – {company}"
            body = generate_email(row)

            try:
                msg = build_message(email, subject, body)
                server.send_message(msg)

                print(f"[{index}] Sent to {email}")

                # Delay (IMPORTANT)
                time.sleep(25)

            except Exception as e:
                print(f"[{index}] Failed: {email} -> {e}")


if __name__ == "__main__":
    main()
