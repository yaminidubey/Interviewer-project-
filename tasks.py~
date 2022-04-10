from mordor import models
import requests
import datetime
import json

from mordor import create_celery_app
celery_object = create_celery_app()


@celery_object.task
def sendRegisterMail(email):
    user = models.User.objects.get(email = email)

    message = {
                'key' : 'fhhMDxOdtA57e0mxlfS8mw',
                'message' :
                {
                    'from_email': 'nishank@zopper.com',
                    'from_name': 'nishank',
                    'headers': {'Reply-To': 'nishank@zopper.com'},
                    'html': '<p>Example HTML content</p>',
                    'important': True,
                    'metadata': {'website': 'www.zopper.com'},
                    'recipient_metadata': [{'rcpt':  user.email,
                                             'values': {'user_id': str(user.id)}}],
                    'subject': 'Thanks for registering at careers.zopper.com',
                    'tags': ['careers-registration'],
                    'text': 'Example text content',
                    'to': [{'email': user.email,
                            'name': user.name,
                            'type': 'to'}]
                },
                'async': False
            }
            
    requests.post('https://mandrillapp.com/api/1.0/messages/send.json', data = json.dumps(message), headers = {"content-type":"application/json"})
