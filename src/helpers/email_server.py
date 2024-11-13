import email
import imaplib
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.clients.bedrock_client import BedrockClient
from src.processors.knowledge_base import KnowledgeBase
from src.processors.query_processor import QueryProcessor
from src.processors.response_generator import ResponseGenerator
from utils import load_config

# Gmail credentials (replace with your email and app-specific password)

GMAIL_USER = 'add-here'

GMAIL_PASSWORD = "add-here"

# Clean and extract text as in original code

text = 'Dear Pawel, [content here]'  # This would be the sample text you provided

cleaned_text = re.sub(r'[\n\r]', '', text)

cleaned_text = cleaned_text.split("Dear Pawel, ")[1]

cleaned_text = cleaned_text.split(" Kind regards")[0]


# Function to send email using Gmail

def send_email(recipient, subject, body):
    msg = MIMEMultipart()

    msg['From'] = GMAIL_USER

    msg['To'] = recipient

    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:

        server = smtplib.SMTP('smtp.gmail.com', 587)

        server.starttls()

        server.login(GMAIL_USER, GMAIL_PASSWORD)

        server.sendmail(GMAIL_USER, recipient, msg.as_string())

        server.quit()

        print("Email sent successfully.")

    except Exception as e:

        print(f"Error sending email: {e}")


# Function to wait for specific emails using Gmail's IMAP

def wait_for_email():
    try:

        # Connect to Gmail's IMAP server

        print("Waiting for new emails...")

        while True:
            print("Starting again...")

            mail = imaplib.IMAP4_SSL('imap.gmail.com')

            mail.login(GMAIL_USER, GMAIL_PASSWORD)

            mail.select("inbox")  # Select the inbox folder
            # Search for unread emails

            status, response = mail.search(None, '(UNSEEN)')

            unread_msg_nums = response[0].split()

            if unread_msg_nums:

                for e_id in unread_msg_nums:

                    # Fetch the email by ID

                    _, response = mail.fetch(e_id, '(RFC822)')

                    raw_email = response[0][1]

                    msg = email.message_from_bytes(raw_email)

                    subject = msg['subject']

                    sender = msg['from']

                    # Extract the email body

                    response = invoke_llm_model(msg, response)

                    print(f"New email received: {subject}")

                    if subject and subject.startswith("Legal Question:"):
                        name = sender.split('<')[0].strip().split('.')[0].capitalize()

                        reply_subject = "RE: " + subject

                        reply_body = f"Dear {name},<br><br>Thank you for your email.<br><br>Best regards,<br>Ellie"

                        send_email(sender, reply_subject, response)

                        print("Response sent.")

                    # Mark the email as read

                    mail.store(e_id, '+FLAGS', '\\Seen')

            # Check for new emails every 5 seconds
            mail.logout()
            time.sleep(5)



    except Exception as e:

        print(f"Error in email fetching: {e}")


def invoke_llm_model(msg, response):
    prompt = ""
    prompt = read_email_body(msg, prompt)
    prompt = prompt.split('Any e-mail message from')[0]

    config = load_config()
    bedrock_client = BedrockClient(config)

    # Initialize Knowledge Bases
    knowledge_bases = {
        'hackathon-team2-eur-lex': KnowledgeBase('eur-lex', config['aws'], bedrock_client),
        'hackathon-team2-legal-acts-austria': KnowledgeBase('legal-acts-austria', config['aws'],
                                                            bedrock_client),
        'hackathon-team2-legal-acts-germany': KnowledgeBase('legal-acts-germany', config['aws'],
                                                            bedrock_client)
    }
    # Initialize Query Processor
    query_processor = QueryProcessor(knowledge_bases)
    # Initialize Response Generator
    response_generator = ResponseGenerator(bedrock_client)
    # Example usage
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    anthropic_version = "bedrock-2023-05-31"
    max_tokens = 512
    temperature = 0.5
    relevant_kb = query_processor.process_query(prompt)
    response = response_generator.generate_response(
        prompt, model_id, anthropic_version, max_tokens, temperature, relevant_kb
    )
    return response


def read_email_body(msg, prompt):
    if msg.is_multipart():

        for part in msg.walk():

            # Check if the part is text or HTML

            if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):

                prompt = part.get_payload(decode=True).decode("utf-8")

                break

            elif part.get_content_type() == "text/html" and not part.get("Content-Disposition"):

                prompt = part.get_payload(decode=True).decode("utf-8")

                break

    else:

        # For non-multipart messages

        prompt = msg.get_payload(decode=True).decode("utf-8")
    return prompt


# Run the function

wait_for_email()
