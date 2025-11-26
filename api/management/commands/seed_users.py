from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Seed dummy users"

    def handle(self, *args, **kwargs):
        if User.objects.count() > 1:
            self.stdout.write(self.style.WARNING("Users already exist, skipping..."))
            return

        for i in range(5):
            User.objects.create_user(
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                password="password123"
            )

        self.stdout.write(self.style.SUCCESS("Users seeded successfully"))
