import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
load_dotenv()

def send_email_aws_ses(subject, body_text, recipient_email):
    # Replace with your credentials or use IAM roles/environment variables
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")

    # Create an SES client
    client = boto3.client(
        'ses',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    try:
        response = client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print("Email sent successfully:", response)
        return {"success": True, "response": response}
    except ClientError as e:
        print("Error sending email:", e.response['Error']['Message'])
        return {"success": False, "error": e.response['Error']['Message']}


