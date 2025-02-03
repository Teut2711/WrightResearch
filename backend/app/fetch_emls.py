import imaplib
import email
from email.header import decode_header


def fetch_eml_files_from_inbox(
    imap_server, imap_port, username, password, mailbox="inbox"
):
    """
    Fetch .eml files from an email inbox using IMAP and save them locally.

    Parameters:
    - imap_server: str - IMAP server address
    - imap_port: int - IMAP server port (usually 993 for SSL)
    - username: str - Email account username
    - password: str - Email account password
    - mailbox: str - Mailbox to fetch emails from (default: 'inbox')

    Returns:
    - List of saved attachment filenames
    """
    saved_files = []
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(username, password)

        mail.select(mailbox)

        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("Failed to search emails.")
            return saved_files

        message_ids = messages[0].split()

        for msg_id in message_ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    print(f"Downloading attachment: {filename}")
                                    with open(filename, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    saved_files.append(filename)
                    else:
                        pass
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Logout from the server
        mail.logout()

    return saved_files


# Dummy credentials and IMAP server settings
IMAP_SERVER = "imap.mail.example.com"
IMAP_PORT = 993
USERNAME = "your_email@example.com"
PASSWORD = "your_password"

# Call the function
saved_files = fetch_eml_files_from_inbox(IMAP_SERVER, IMAP_PORT, USERNAME, PASSWORD)
