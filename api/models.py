from django.db import models
from django.contrib.auth.models import User

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