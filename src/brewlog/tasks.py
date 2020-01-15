import logging
import os
import sys
from typing import Optional, Sequence

import requests

_mailgun_domain = os.getenv('MAILGUN_DOMAIN')
_mailgun_api_url = f'https://api.eu.mailgun.net/v3/{_mailgun_domain}/messages'
_mailgun_auth = ('api', os.getenv('MAILGUN_API_KEY'))

logger = logging.getLogger('rq.worker')


def send_email(
            sender: str, recipients: Sequence[str], subject: str,
            html_body: str, text_body: Optional[str] = None,
        ):
    try:
        data = {
            'from': sender,
            'to': recipients,
            'subject': subject,
            'html': html_body,
        }
        if text_body is not None:
            data['text'] = text_body
        requests.post(_mailgun_api_url, auth=_mailgun_auth, data=data)
    except Exception:
        logger.error(
            'Unhandled exception in background task', exc_info=sys.exc_info()
        )
