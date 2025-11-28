import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import FinanceManagement


class Command(BaseCommand):
    help = "Seed finance management data"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("Users missing."))
            return

        for user in users:
            FinanceManagement.objects.create(
                user=user,
                base_salary=random.randint(7_000_000, 12_000_000),
                spouse_allowance=random.randint(0, 1) * 500_000,
                child_allowance=random.randint(0, 2) * 300_000,
                bpjs_health_percentage=1.00,
                bpjs_employment_percentage=2.00,
                tax_amount=random.choice([5, 10]),
                overtime_hours=random.randint(0, 20),
                receivable_amount=random.randint(0, 1_000_000),
            )

        self.stdout.write(self.style.SUCCESS("FinanceManagement seeded successfully"))
