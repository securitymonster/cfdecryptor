import datetime
import logging
import os
import azure.functions as func


def get_env_var(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        logging.error(f"Environment variable {name} not found.")
        return ""


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')
        logging.info(
            f'The value of event_hub_name is {get_env_var("EVENT_HUB_NAME")}')

    logging.info(f'Python timer trigger function ran at {utc_timestamp}')
