from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from api.models import SalarySlip, FinanceManagement


class Command(BaseCommand):
    help = "Seed salary slip for all employees"

    def add_arguments(self, parser):
        parser.add_argument(
            "--months",
            type=int,
            default=3,
            help="Jumlah bulan slip gaji yang ingin dibuat (default: 3)",
        )

    def handle(self, *args, **options):
        months_back = options["months"]
        now = datetime.now()

        employees = FinanceManagement.objects.select_related("user")

        if not employees:
            self.stdout.write(self.style.ERROR("No FinanceManagement data found!"))
            return

        created = 0
        skipped = 0

        for finance in employees:
            for i in range(months_back):
                date = now - timedelta(days=30 * i)
                year = date.year
                month = date.month

                slip, flag = SalarySlip.objects.get_or_create(
                    user=finance.user,
                    finance=finance,
                    year=year,
                    month=month,
                )

                if flag:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"SalarySlip seeding completed! Created: {created}, Skipped: {skipped}"
            )
        )
