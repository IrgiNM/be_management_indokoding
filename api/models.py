from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class SiteSetting(models.Model):
    category = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    value = models.TextField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("category", "key")
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"
        ordering = ("category", "key")

    def __str__(self):
        return f"{self.category} - {self.key}"


class Employee(models.Model):
    EMPLOYMENT_STATUS = (
        ("active", "Active"),
        ("resigned", "Resigned"),
        ("terminated", "Terminated"),
        ("probation", "Probation"),
    )

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")

    employee_id = models.CharField(max_length=20, unique=True)

    # Personal Information
    full_name = models.CharField(max_length=150)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    tax_number = models.CharField(max_length=30, null=True, blank=True)
    identity_number = models.CharField(max_length=30, null=True, blank=True)

    # Contact
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    # Job Information
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    join_date = models.DateField()
    resign_date = models.DateField(null=True, blank=True)

    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default="active")

    # Emergency Contact
    emergency_name = models.CharField(max_length=150, null=True, blank=True)
    emergency_phone = models.CharField(max_length=20, null=True, blank=True)
    emergency_relation = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    # Helper Methods
    def is_active(self):
        return self.employment_status == "active"


class BankAccount(models.Model):
    BANK_CHOICES = [
        ("BCA", "Bank Central Asia (BCA)"),
        ("BNI", "Bank Negara Indonesia (BNI)"),
        ("BRI", "Bank Rakyat Indonesia (BRI)"),
        ("MANDIRI", "Bank Mandiri"),
        ("CIMB", "CIMB Niaga"),
        ("BTN", "Bank Tabungan Negara (BTN)"),
        ("DANAMON", "Bank Danamon"),
        ("PERMATA", "Bank Permata"),
        ("OTHER", "Bank Lainnya"),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="bank_accounts")

    bank_name = models.CharField(max_length=50, choices=BANK_CHOICES)
    account_number = models.CharField(max_length=50)
    account_holder = models.CharField(max_length=150)

    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        ordering = ["employee", "-is_primary"]

    def __str__(self):
        return f"{self.employee.full_name} - {self.bank_name} ({self.account_number})"

    def save(self, *args, **kwargs):
        # pastikan hanya 1 rekening utama
        if self.is_primary:
            BankAccount.objects.filter(
                employee=self.employee, is_primary=True
            ).update(is_primary=False)

        super().save(*args, **kwargs)

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
        overtime_rate = self.base_salary / Decimal(173)
        overtime_pay = self.overtime_hours * overtime_rate

        # Gross salary
        gross = (
                self.base_salary +
                Decimal(self.spouse_allowance) +
                Decimal(self.child_allowance) +
                overtime_pay
        )
        self.gross_salary = gross

        # BPJS
        bpjs_health = gross * (Decimal(self.bpjs_health_percentage) / Decimal(100))
        bpjs_employment = gross * (Decimal(self.bpjs_employment_percentage) / Decimal(100))

        # Tax
        tax = gross * (self.tax_amount / Decimal(100))

        # Net Salary
        net = gross - (bpjs_health + bpjs_employment + tax) - self.receivable_amount
        self.net_salary = net

        super().save(*args, **kwargs)


class SalarySlip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    finance = models.ForeignKey(FinanceManagement, on_delete=models.CASCADE)

    year = models.IntegerField()
    month = models.IntegerField()

    gross_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bpjs_health = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bpjs_employment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "year", "month")
        verbose_name = "Salary Slip"
        verbose_name_plural = "Salary Slips"

    def __str__(self):
        return f"Slip Gaji {self.user.username} - {self.month}/{self.year}"

    def calculate(self):
        """Hitung salary dari FinanceManagement"""
        base = Decimal(self.finance.base_salary)
        spouse = Decimal(self.finance.spouse_allowance)
        child = Decimal(self.finance.child_allowance)
        gross = base + spouse + child

        bpjs_health = gross * (Decimal(self.finance.bpjs_health_percentage) / Decimal("100"))
        bpjs_employment = gross * (Decimal(self.finance.bpjs_employment_percentage) / Decimal("100"))
        tax = gross * (Decimal(self.finance.tax_amount) / Decimal("100"))
        overtime_pay = Decimal(self.finance.overtime_hours) * Decimal("20000")

        net = gross + overtime_pay - (bpjs_health + bpjs_employment + tax)

        self.gross_salary = gross
        self.bpjs_health = bpjs_health
        self.bpjs_employment = bpjs_employment
        self.tax_amount = tax
        self.overtime_pay = overtime_pay
        self.net_salary = net

    def save(self, *args, **kwargs):
        self.calculate()
        super().save(*args, **kwargs)
