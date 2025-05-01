from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from patientsystem.models import UserProfile

class Command(BaseCommand):
    help = 'Creates a neurologist user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the neurologist')
        parser.add_argument('email', type=str, help='Email for the neurologist')
        parser.add_argument('password', type=str, help='Password for the neurologist')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # The signal will create the UserProfile automatically
        # We just need to update the role
        user_profile = UserProfile.objects.get(user=user)
        user_profile.role = 'neurologist'
        user_profile.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created neurologist user: {username}')) 