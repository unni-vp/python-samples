""" Module containing methods for interacting with Twilio services """

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

import re
import logging
import sys

app = Flask(__name__)

# Add System out and File loggers.
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().addHandler(logging.FileHandler("app.log"))

# Initialize Twilio credentials, server host and port details from environment variables
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
fromNumber = os.environ['FROM_NUMBER']
statusURL = "http://" + os.environ['HOST'] + ":" + os.environ['PORT'] + "/sms/status"


@app.route("/sms/callback", methods=['GET', 'POST'])
def sms_incoming():

    """ API method to handle callback for incoming messages to Twilio Phone number """
    
    # Get the message details for the incoming message recevied at Twilio number
    body = request.values.get('Body', None)
    sender = request.values.get('From', None)
    senderCity = request.values.get('FromCity', None)
    senderCountry = request.values.get('FromCountry', None)
    myNumber = request.values.get('To', None)

    logging.debug("Message recieved from {} : {}, {} : {}".format(sender, senderCity, senderCountry, body))

    # Check if the message text contains a Phone number
    regex = re.compile("\+?\d[\( -]?\d{3}[\) -]?\d{3}[ -]?\d{2}[ -]?\d{2}")
    phoneNumbers = re.findall(regex, body)

    # If phone number present in message, forward the message to that number
    if phoneNumbers:
        message = "Thanks for your Message. We have also forwarded the message to {}".format(phoneNumbers[0])
        send_message(phoneNumbers[0], body)
    else:
        message = "Thanks for your Message. I hope to visit {} soon.\n\nSent From: {}.".format(senderCity, myNumber)

    # Provide a reply to sender for incoming message
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)


@app.route("/sms", methods=['POST'])
def sms_send():
    
    """ API method to send a message from the Twilio Phone number to a destination phone """

    # Get the destination number and message body from request
    request_data = request.get_json()
    toNumber = request_data['toNumber']
    body = request_data['body']

    logging.debug("Sending message: {} - {}".format(toNumber, body))

    # Send message using Twilio client
    send_message(toNumber, body)


def send_message(toNumber, body):

    """ Send message to destination number from Twilio Phone number """

    try:
        # Create the Twilio sms client
        client = Client(account_sid, auth_token)

        # Send the message; also specifying a callback for status updates
        message = client.messages.create(body= body, from_= fromNumber, to= toNumber, status_callback= statusURL)

        return ("Message sent succesfully : " + message.sid, 201)

    except Exception as e: 
        logging.error("Error while sending message: {}".format(e))
        return ("Message sending failed", 204)


@app.route("/sms", methods=['GET'])
def sms_list():

    """ API method to fetch all messages sent from the Twilio Phone number """

    sms_list = []
    try:
        # Create the Twilio sms client
        client = Client(account_sid, auth_token)
        
        # Fetch and populate the message list
        for sms in client.messages.list():
            msg_entry = "\t".join([sms.sid, sms.from_, sms.to, sms.direction, sms.status])
            logging.debug("Message entry: {}".format(msg_entry))
            sms_list.append(msg_entry)
     
    except Exception as e: 
        logging.error("Error while sending message: {}".format(e))
    
    return "\n".join(sms_list)


@app.route("/sms/status", methods=['POST'])
def listen_sms_status():

    """ API method to handle status update callback for messages sent from the Twilio Phone number """
    
    # Get the details of message and its current status from the callback request
    message_sid = request.values.get('MessageSid', None)
    message_status = request.values.get('MessageStatus', None)

    # Log the status update. Implement any other action as required.
    logging.info("Status recieved -- SID: {}, Status: {}".format(message_sid, message_status))

    return ('', 204)


if __name__ == "__main__":
    app.run(debug=True)