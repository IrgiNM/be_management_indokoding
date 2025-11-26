from django.core.management.base import BaseCommand
from api.models import SiteSetting


class Command(BaseCommand):
    help = "Seed global site settings (category, key, value)"

    DEFAULT_SETTINGS = [
        ("general", "site_name", "HR & Payroll System"),
        ("general", "company_name", "PT Teknologi Indonesia"),
        ("general", "company_email", "admin@company.com"),

        ("payroll", "bpjs_health_percentage", "1.0"),
        ("payroll", "bpjs_employment_percentage", "2.0"),
        ("payroll", "tax_percentage", "5.0"),

        ("feature", "enable_notifications", "true"),
        ("feature", "auto_salary_slip", "true"),
    ]

    def handle(self, *args, **kwargs):
        created_count = 0

        for category, key, value in self.DEFAULT_SETTINGS:
            obj, created = SiteSetting.objects.get_or_create(
                category=category,
                key=key,
                defaults={"value": value}
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {created_count} site settings"
        ))
