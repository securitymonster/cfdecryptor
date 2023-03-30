import datetime
import logging
import os
import azure.functions as func
event_hub_name = os.environ.get('EVENT_HUB_NAME')


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
