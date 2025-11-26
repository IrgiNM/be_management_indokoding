import random
import decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Reimbursement, ReimbursementItems, Category


class Command(BaseCommand):
    help = "Seed reimbursements with items"

    def handle(self, *args, **kwargs):
        users = list(User.objects.all())
        categories = list(Category.objects.all())

        if not users or not categories:
            self.stdout.write(self.style.ERROR("Users or Categories missing."))
            return

        reimbursements = []

        # Create reimbursements
        for _ in range(10):
            user = random.choice(users)
            reimb = Reimbursement.objects.create(
                user=user,
                title=f"Reimbursement {random.randint(100, 999)}",
                description="Dummy reimbursement entry.",
                total_amount=0,
                status=random.choice(["Pending", "Approved", "Rejected"])
            )
            reimbursements.append(reimb)

        # Create items
        for reimb in reimbursements:
            total = decimal.Decimal(0)

            for _ in range(random.randint(1, 5)):
                cat = random.choice(categories)
                amount = decimal.Decimal(random.randint(50_000, 500_000))

                ReimbursementItems.objects.create(
                    reimbursement=reimb,
                    category=cat,
                    item_amount=amount
                )
                total += amount

            reimb.total_amount = total
            reimb.save()

        self.stdout.write(self.style.SUCCESS("Reimbursements & items seeded successfully"))
