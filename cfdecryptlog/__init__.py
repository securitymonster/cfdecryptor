# Default stuff:
# import logging

# import azure.functions as func


# def main(myblob: func.InputStream):
#     logging.info(f"Python blob trigger function processed blob \n"
#                  f"Name: {myblob.name}\n"
#                  f"Blob Size: {myblob.length} bytes")


import os
import json
import base64
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData
from azure.storage.blob import BlobServiceClient

from pyhpke import AEADId, CipherSuite, KDFId, KEMId, KEMKey

suite_r = CipherSuite.new(KEMId.DHKEM_X25519_HKDF_SHA256,
                          KDFId.HKDF_SHA256, AEADId.CHACHA20_POLY1305)

private_key = base64.b64decode(os.environ["PRIVATE_KEY"])

def process_logfile_line(line):
    logline_dict = json.loads(line)

    if "Metadata" in logline_dict:
        if "encrypted_matched_data" in logline_dict["Metadata"]:
            matched_data = base64.b64decode(logline_dict["Metadata"]["encrypted_matched_data"])
            encapped_key = matched_data[1:33]
            ciphertext = matched_data[41:]

            skr = suite_r.kem.deserialize_private_key(private_key)
            recipient = suite_r.create_recipient_context(encapped_key, skr)

            try:
                plaintext_bytes = recipient.open(ciphertext)
                plaintext = plaintext_bytes.decode('utf-8')
                plaintext_dict = json.loads(plaintext)
                logline_dict['Metadata']["decrypted_matched_data"] = plaintext_dict

            except Exception as e:
                logline_dict['Metadata'].update({
                    "decrypted_matched_data": {
                        "decryption": "failed"
                    }
                })

    return json.dumps(logline_dict)


def main(event: func.EventGridEvent, blob: func.InputStream):
    blob_data = blob.read().decode('utf-8')
    payload_list = list(map(process_logfile_line, blob_data.split('\n')))

    connection_str = os.environ["EVENT_HUB_CONN_STR"]
    eventhub_name = os.environ["EVENT_HUB_NAME"]

    producer = EventHubProducerClient.from_connection_string(connection_str, eventhub_name=eventhub_name)
    with producer:
        for payload_str in payload_list:
            event_data = EventData(payload_str)
            producer.send(event_data)

    return func.HttpResponse(f"Processed blob: {blob.name}.", status_code=200)


