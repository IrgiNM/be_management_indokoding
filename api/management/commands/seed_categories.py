from django.core.management.base import BaseCommand
from api.models import Category


class Command(BaseCommand):
    help = "Seed reimbursement categories"

    CATEGORIES = [
        "Transport",
        "Makan / Konsumsi",
        "Akomodasi",
        "Perjalanan Dinas",
        "Peralatan Kerja",
        "Kesehatan",
        "Lembur",
        "Penggantian Barang",
        "Operasional Kantor",
        "Lainnya",
    ]

    def handle(self, *args, **kwargs):
        for name in self.CATEGORIES:
            Category.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS("Categories seeded successfully"))
