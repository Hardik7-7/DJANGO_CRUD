from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from myapp.models import AccessToken 

class Command(BaseCommand):
    help = 'Deletes access tokens that have been expired for more than 10 minutes'

    def handle(self, *args, **kwargs):
        expiration_time = timedelta(minutes=10)
        cutoff_time = timezone.now() - expiration_time

        expired_tokens = AccessToken.objects.filter(
            created_at__lt=cutoff_time,
        )

        deleted_count = expired_tokens.delete()[0]

        print(f'Successfully deleted {deleted_count} expired tokens')