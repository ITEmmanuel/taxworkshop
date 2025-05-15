from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create test users emmanuel and zhoum with default passwords.'

    def handle(self, *args, **options):
        users = [
            {'username': 'emmanuel', 'email': 'emmanuel@example.com', 'password': 'testpass123'},
            {'username': 'zhoum', 'email': 'zhoum@example.com', 'password': 'testpass123'},
        ]
        for user in users:
            if not User.objects.filter(username=user['username']).exists():
                User.objects.create_user(
                    username=user['username'],
                    email=user['email'],
                    password=user['password']
                )
                self.stdout.write(self.style.SUCCESS(f"User '{user['username']}' created with password 'testpass123'"))
            else:
                self.stdout.write(self.style.WARNING(f"User '{user['username']}' already exists."))
