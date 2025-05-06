import pandas as pd
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import glob
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_email_alert(api_key, sender_email, recipient_emails, days_threshold=7):
    """Send an email alert with upcoming auction deadlines to multiple recipients."""
    try:
        # Validate inputs
        if not api_key or not sender_email or not recipient_emails:
            logger.error("Missing required environment variables: SENDGRID_API_KEY, SENDER_EMAIL, or RECIPIENT_EMAILS")
            return False

        # Ensure recipient_emails is a list
        if isinstance(recipient_emails, str):
            recipient_emails = [email.strip() for email in recipient_emails.split(',')]

        # Validate email addresses (basic check)
        if not all('@' in email for email in recipient_emails):
            logger.error("Invalid email address in recipient list: %s", recipient_emails)
            return False

        # Find the latest processed CSV file
        csv_files = glob.glob("auction_exports/processed_auctions_*.csv")
        if not csv_files:
            logger.error("No processed auction data found for email.")
            return False

        latest_csv = max(csv_files, key=os.path.getctime)
        df = pd.read_csv(latest_csv)

        # Filter for auctions with days_until_submission <= threshold
        if 'days_until_submission' in df.columns:
            upcoming_df = df[df['days_until_submission'] <= days_threshold]
            upcoming_df = upcoming_df.sort_values(by='days_until_submission')
        else:
            logger.error("Column 'days_until_submission' not found in the data.")
            return False

        # Create email content
        subject = "IBBI Auction Alerts - Upcoming Deadlines"
        if upcoming_df.empty:
            body = "No auctions with submission deadlines within the next 7 days."
        else:
            body = "The following auctions have submission deadlines within the next 7 days:\n\n"
            body += upcoming_df.to_string(index=False)
            body += "\n\nTotal upcoming auctions: " + str(len(upcoming_df))

        # Set up the email
        message = Mail(
            from_email=sender_email,
            to_emails=recipient_emails,  # SendGrid accepts a list of emails
            subject=subject,
            plain_text_content=body
        )

        # Send the email via SendGrid
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info("Email sent successfully to %s. Status code: %s", recipient_emails, response.status_code)
        return True

    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False

if __name__ == "__main__":
    # Retrieve environment variables
    api_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")
    recipient_emails = os.getenv("RECIPIENT_EMAILS")
    
    # Send the email alert
    send_email_alert(api_key, sender_email, recipient_emails)