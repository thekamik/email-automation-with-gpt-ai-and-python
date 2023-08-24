import smtplib, ssl
import time
import imaplib
import email
import openai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class mail_bot:
    def __init__(self, api_key, api_role, sender, mail_host, password, sender_email, sent_folder, inbox_folder, IMAP_SSL, SMTP_SSL):
        self.api_key = api_key
        self.api_role = api_role
        self.sender = sender
        self.mail_host = mail_host
        self.password = password
        self.sender_email = sender_email
        self.sent_folder = sent_folder
        self.inbox_folder = inbox_folder
        self.IMAP_SSL = IMAP_SSL
        self.SMTP_SSL = SMTP_SSL
    
    def reply_to_emails(self, unread_messages: bool):
        # Unread mails
        unread_mails = [[], [], [], []]

        # Connect to the mailbox
        mail = imaplib.IMAP4_SSL(self.mail_host)
        mail.login(self.sender_email, self.password)
        mail.select(self.inbox_folder)

        # Search for unread emails in the mailbox
        status, messages = mail.search(None, 'UNSEEN' if unread_messages else 'ALL')
        message_ids = messages[0].split()

        for msg_id in message_ids:
            # Fetch the email
            status, data = mail.fetch(msg_id, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Extract email details
            sender = email_message['From']
            subject = email_message['Subject']
            date = email_message['Date']

            #Get the email body content
            body = self.get_email_body(email_message)

            # Generate answer with gpt
            new_body = mail_operator.ai_responder(body)

            # Send email
            mail_operator.send_email(subject=subject, body=new_body, receiver_email=sender)

        mail.logout()
        return unread_mails
    
    def get_email_body(self, email_message):
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content = part.get_content_type()
                disposition = str(part.get('Content-Disposition'))
                if content == 'text/plain' and 'attachment' not in disposition:
                    body = part.get_payload(decode=True) 
                    break
        else:
            body = email_message.get_payload(decode=True)

        return body
    
    def send_email(self, subject, body, receiver_email):
        
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        # Add body to email
        message.attach(MIMEText(str(body), "plain"))

        # Add attachment to message and convert message to string
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.mail_host, self.SMTP_SSL, context=context) as server:
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, receiver_email, text)

        # Add email to send folder, and mark email as seen
        imap = imaplib.IMAP4_SSL(self.mail_host, self.IMAP_SSL)
        imap.login(self.sender_email, self.password)
        imap.append(self.sent_folder, '\\Seen', imaplib.Time2Internaldate(time.time()), text.encode('utf8'))
        imap.logout()
    
    def ai_responder(self, message):
        
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        messages=[
            {
                "role": "system",
                "content": self.api_role
            },
            {
                "role": "user",
                "content": str(message)
            }
        ],
        temperature=0.8,
        max_tokens=256
        )

        # Return generated message
        my_openai_obj = list(response.choices)[0]
        return (my_openai_obj.to_dict()['message']['content'])
        

if __name__ == "__main__":

    # Private Variables (replace this with your data)
    new_api_key = "Your api key"
    new_mail_host = "Your mail host"
    new_password = "Your e-mail password"
    new_your_email = "Your e-mail address"

    # GPT variables
    new_api_role = "You are a service assistant. You try to solve problems."

    # Email Variables
    new_subject = "generated answer with GPT BOT"
    new_sender = "GPT BOT"    
    new_sent_folder = 'SENT'
    new_inbox_folder = 'INBOX'
    new_SMTP_SSL = 465
    new_IMAP_SSL = 993 
    

    # Instance of bot class
    mail_operator = mail_bot(
        new_api_key, 
        new_api_role, 
        new_sender, 
        new_mail_host, 
        new_password, 
        new_your_email, 
        new_sent_folder, 
        new_inbox_folder, 
        new_IMAP_SSL, 
        new_SMTP_SSL 
    )

    # Here we read all messages
    unread_messages = mail_operator.reply_to_emails(unread_messages=True)
        
    print("done")
