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


def create_server():
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    return server


def main():
    df = pd.read_csv(CSV_FILE)

    df = df.dropna(subset=["Email"])
    df["Email"] = df["Email"].str.strip().str.lower()
    df = df.drop_duplicates(subset=["Email"])

    print(f"Total emails after cleaning: {len(df)}")

    server = create_server()
    sent_count = 0

    for index, row in df.iterrows():
        email = row["Email"]
        company = str(row.get("Company", "")).strip()

        subject = f"Application: Backend, AI Systems & SaaS Engineering – {company}"
        body = generate_email(row)

        try:
            msg = build_message(email, subject, body)
            server.send_message(msg)

            print(f"[{index}] Sent to {email}")
            sent_count += 1

            # 🔥 Reconnect every 30 emails (CRITICAL FIX)
            if sent_count % 30 == 0:
                print("Reconnecting SMTP...")
                server.quit()
                time.sleep(5)
                server = create_server()

            time.sleep(5)

        except Exception as e:
            print(f"[{index}] Failed: {email} -> {e}")

            # 🔥 Try reconnect on failure
            try:
                server.quit()
            except:
                pass

            time.sleep(5)
            server = create_server()

    server.quit()


if __name__ == "__main__":
    main()
