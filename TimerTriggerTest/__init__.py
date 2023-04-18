import os
import json
import datetime
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData

EVENT_HUB_CONNECTION_STRING = os.environ['EVENT_HUB_CONNECTION_STRINGING']
EVENT_HUB_NAME = os.environ['EVENT_HUB_NAME']


# EVENT_HUB_NAME = "payloadlogs"
# EVENT_HUB_CONN_STRING = "Endpoint=sb://payloadlogs.servicebus.windows.net/;SharedAccessKeyName=payloadsend;SharedAccessKey=ikZlmGSwTi69BmU1PjY9JbL6xtmIA9mmC+AEhPmv5aw="

def main(mytimer: func.TimerRequest) -> None:
    # Create a producer client to send messages to the event hub
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STRING, eventhub_name=EVENT_HUB_NAME
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
