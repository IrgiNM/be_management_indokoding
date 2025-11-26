from django.db import models
from django.contrib.auth.models import User
import decimal

class Reimbursement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField()
    image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending')

    def __str__(self):
        return f"{self.created_at} - user: {self.user.username} = Rp.{self.total_amount}"
    
class Category(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ReimbursementItems(models.Model):
    reimbursement = models.ForeignKey(Reimbursement, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} = Rp.{self.item_amount}"
    
class FinanceManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)  # Gaji pokok
    spouse_allowance = models.IntegerField(default=0)  # Tunjangan istri
    child_allowance = models.IntegerField(default=0)   # Tunjangan anak
    bpjs_health_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)   # BPJS Kesehatan (%)
    bpjs_employment_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # BPJS Ketenagakerjaan (%)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Pajak (%)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)  # Overtime hours
    receivable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Piutang (Receivable)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Finance data for {self.user.username}"

    def save(self, *args, **kwargs):
        # Overtime pay
        overtime_rate = self.base_salary / decimal.Decimal(173)
        overtime_pay = self.overtime_hours * overtime_rate

        # Gross salary
        gross = (
                self.base_salary +
                decimal.Decimal(self.spouse_allowance) +
                decimal.Decimal(self.child_allowance) +
                overtime_pay
        )
        self.gross_salary = gross

        # BPJS
        bpjs_health = gross * (decimal.Decimal(self.bpjs_health_percentage) / decimal.Decimal(100))
        bpjs_employment = gross * (decimal.Decimal(self.bpjs_employment_percentage) / decimal.Decimal(100))

        # Tax
        tax = gross * (self.tax_amount / decimal.Decimal(100))

        # Net Salary
        net = gross - (bpjs_health + bpjs_employment + tax) - self.receivable_amount
        self.net_salary = net

        super().save(*args, **kwargs)
