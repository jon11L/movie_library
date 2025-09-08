from typing import Any
from rest_framework.authtoken.models import Token

from django.core.management.base import BaseCommand, CommandParser
from user.models import User



class Command(BaseCommand):
    help = 'small custom command to call with a specific user to create a token for Rest API'

    def handle(self, *args: Any, **options: Any) -> str | None:

        user = User.objects.get(username="jon")
        token = Token.objects.create(user=user)
        print(token.key)
        # return super().handle(*args, **options)