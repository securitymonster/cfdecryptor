import os
import json
import datetime
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData

EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONNECTION_STRING']
EVENT_HUB_NAME = os.environ['EVENT_HUB_NAME']


def main(mytimer: func.TimerRequest) -> None:
    # Create a producer client to send messages to the event hub
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME
    )

    # Create a message to send
    message = {"foo": "bar", "baz": 42}
    message_bytes = json.dumps(message).encode("utf-8")

    # Create an event data object from the message
    event_data = EventData(message_bytes)

    # Send the event data to the event hub
    with producer:
        producer.send(event_data)

    print('Message sent to event hub')


def timer_triggered(timer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    print(f'{utc_timestamp}: timer triggered.')


# Schedule to trigger every 10 seconds
schedule = '*/10 * * * * *'
