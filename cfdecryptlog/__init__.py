# Default stuff:
# import logging

# import azure.functions as func


# def main(myblob: func.InputStream):
#     logging.info(f"Python blob trigger function processed blob \n"
#                  f"Name: {myblob.name}\n"
#                  f"Blob Size: {myblob.length} bytes")

import logging
import os
import json
import base64
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData
from azure.storage.blob import BlobServiceClient
from pyhpke import AEADId, CipherSuite, KDFId, KEMId, KEMKey

import random
import datetime
import time

suite_r = CipherSuite.new(KEMId.DHKEM_X25519_HKDF_SHA256,
                          KDFId.HKDF_SHA256, AEADId.CHACHA20_POLY1305)

private_key = base64.b64decode(os.environ["PRIVATE_KEY"])


def process_logfile_line(line):
    # Read the log line, which is a JSON string, into a dict
    logline_dict = json.loads(line)

    # Only do this if there is any metadata
    if "Metadata" in logline_dict:
        if "encrypted_matched_data" in logline_dict["Metadata"]:
            # The encrypted_matched_data is a base64 encoded JSON string. So decode and load in dict
            matched_data = base64.b64decode(
                logline_dict["Metadata"]["encrypted_matched_data"])
            # Some dirty splicing is needed, because originally the object is a RUST object
            # encapped_key is the HPKE shared key
            encapped_key = matched_data[1:33]
            ciphertext = matched_data[41:]

            skr = suite_r.kem.deserialize_private_key(private_key)
            recipient = suite_r.create_recipient_context(encapped_key, skr)

            try:
                plaintext_bytes = recipient.open(ciphertext)
                plaintext = plaintext_bytes.decode('utf-8')
                plaintext_dict = json.loads(plaintext)
                # Take the existing logline JSON dict and add the decrypted data to a new JSON key "decrypted_matched_data" below the existing "Metadata"
                # Note that the encrypted data is kept in the JSON object for anti-tampering control (might change in the future)
                logline_dict['Metadata']["decrypted_matched_data"] = plaintext_dict

            except Exception as e:
                logline_dict['Metadata'].update({
                    "decrypted_matched_data": {
                        "decryption": "failed"
                    }
                })

    return json.dumps(logline_dict)


def main(mytimer: func.TimerRequest) -> None:
    # Generate random data for the JSON object
    date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    colors = ["red", "green", "blue", "yellow", "orange"]
    fruits = ["apple", "banana", "orange", "kiwi", "strawberry"]
    fruit_color = random.choice(colors)
    fruit_name = random.choice(fruits)

    # Create the JSON object
    data = {
        "date": date,
        "fruit-color": fruit_color,
        "fruit-name": fruit_name
    }
    payload_str = json.dumps(data)

    # Send the JSON object to the Event Hub
    connection_str = os.environ["EVENT_HUB_CONN_STR"]
    eventhub_name = os.environ["EVENT_HUB_NAME"]
    producer = EventHubProducerClient.from_connection_string(
        connection_str, eventhub_name=eventhub_name)
    with producer:
        event_data = EventData(payload_str)
        producer.send(event_data)

    return
