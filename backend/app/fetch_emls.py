import imaplib
import email
import os
from email.header import decode_header
from dotenv import load_dotenv
import logging

# Load environment variables from a .env file
load_dotenv()

# Gmail IMAP settings
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
USERNAME = os.getenv("IMAP_USERNAME")
PASSWORD = os.getenv("IMAP_PASSWORD")
SAVE_DIR = os.getenv("SAVE_DIR", "data/emls")

# Configure logging
logger = logging.getLogger("uvicorn")


def decode_mime_words(s):
    """Decode MIME-encoded words in email headers."""
    decoded = decode_header(s)
    return "".join(
        part.decode(enc or "utf-8") if isinstance(part, bytes) else part
        for part, enc in decoded
    )


def fetch_gmail_emails(limit=10):
    """Fetch up to `limit` unread emails and save them as .eml files."""

    logger.info("Fetching emails from inbox...")

    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(USERNAME, PASSWORD)
        mail.select("inbox")

        # Search for unread emails
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            logger.info("No unread emails found.")
            return

        msg_ids = messages[0].split()[:limit]

        for msg_id in msg_ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_mime_words(msg["Subject"])
                    filename = os.path.join(SAVE_DIR, f"{msg_id.decode()}.eml")

                    # Save email as .eml
                    with open(filename, "wb") as f:
                        f.write(response_part[1])

                    logger.info(f"Saved: {filename} (Subject: {subject})")

        mail.logout()
    except Exception as e:
        logger.error(f"Error: {e}")


# Fetch only 10 emails
fetch_gmail_emails(10)
