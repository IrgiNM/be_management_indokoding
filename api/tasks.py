from datetime import datetime

from celery import shared_task

from api.models import FinanceManagement, SalarySlip


@shared_task
def auto_generate_salary_slips():
    """Generate slip gaji untuk seluruh karyawan tiap bulan."""

    now = datetime.now()
    year = now.year
    month = now.month

    employees = FinanceManagement.objects.filter(is_active=True).select_related("user")

    created = 0
    skipped = 0

    for finance in employees:
        slip, flag = SalarySlip.objects.get_or_create(
            user=finance.user,
            finance=finance,
            year=year,
            month=month
        )
        if flag:
            created += 1
        else:
            skipped += 1

    return f"Created: {created}, Skipped: {skipped}"
