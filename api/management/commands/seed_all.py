from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run all seeders: users, categories, reimbursements, finance"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("=== Running Full Seeder ==="))

        call_command("seed_users")
        call_command("seed_categories")
        call_command("seed_reimbursements")
        call_command("seed_finance")

        self.stdout.write(self.style.SUCCESS("=== All seeding completed! ==="))
