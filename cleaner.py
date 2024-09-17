import imaplib
import email
import configparser
from email.header import decode_header

# Load email credentials from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

EMAIL_ADDRESS = config.get('credentials', 'email_address')
EMAIL_PASSWORD = config.get('credentials', 'email_password')

# Connect to Gmail's IMAP server
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

# Select the inbox folder (read/write mode)
mail.select("inbox")

# Search for emails from a specific sender
status, messages = mail.search(None, 'FROM', 'notifications@acquire.com')

# Check if search returned any emails
if status == "OK":
    email_ids = messages[0].split()

    if not email_ids:
        print("No emails found from the specified sender.")
    else:
        for email_id in email_ids:
            # Fetch the email by ID
            res, msg = mail.fetch(email_id, '(RFC822)')
            
            for response_part in msg:
                if isinstance(response_part, tuple):
                    # Parse the email
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    
                    # Decode the subject
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Debug: Print the subject of each email
                    print(f"Processing email with subject: {subject}")
                    
                    # Mark the email for deletion (remove the 'keyword' check)
                    mail.store(email_id, '+FLAGS', '\\Deleted')
                    print(f"Email with subject '{subject}' marked for deletion.")
        
        # Permanently delete emails marked for deletion
        mail.expunge()
        print("Marked emails have been deleted.")
else:
    print("Failed to retrieve emails.")

# Logout from the mail server
mail.logout()
