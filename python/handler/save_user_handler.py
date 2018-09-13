from thundra.thundra_agent import Thundra
from random import randint
import time

from user.user_service import UserService

thundra = Thundra()
user_service = UserService()


@thundra
def save_user_handler(event, context):
    user = user_service.save_user(event['name'], event['surname'], event['id'])
    response = {}
    if user is not None:
        response['Name of The User'] = user.name
        response['Surname of The User'] = user.surname
    time.sleep(randint(0, 7))
    print(user)
    return response
