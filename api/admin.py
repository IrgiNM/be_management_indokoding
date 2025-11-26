import csv
import decimal
from django.contrib import admin, messages
from django.http import HttpResponse
from openpyxl import Workbook

from .models import (
    Reimbursement, Category, ReimbursementItems, FinanceManagement
)


# ============================================================
# ===============  DASHBOARD CUSTOM ADMIN SITE  ===============
# ============================================================

class FinanceAdminSite(admin.AdminSite):
    site_header = "Finance Management Dashboard"
    site_title = "Finance Admin"
    index_title = "Finance Management Overview"

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context["total_reimbursements"] = Reimbursement.objects.count()
        extra_context["pending_reimb"] = Reimbursement.objects.filter(status="Pending").count()
        extra_context["approved_reimb"] = Reimbursement.objects.filter(status="Approved").count()
        extra_context["total_finance_records"] = FinanceManagement.objects.count()

        return super().index(request, extra_context=extra_context)


finance_admin_site = FinanceAdminSite(name="finance_admin")


# ============================================================
# ===================== INLINE ITEMS =========================
# ============================================================

class ReimbursementItemsInline(admin.TabularInline):
    model = ReimbursementItems
    extra = 1
    autocomplete_fields = ['category']
    readonly_fields = ('created_at', 'updated_at')


# ============================================================
# ==================== UTIL FUNCTIONS ========================
# ============================================================

def update_total_amount(reimbursement):
    """Hitung total_amount dari semua items."""
    items = ReimbursementItems.objects.filter(reimbursement=reimbursement)
    total = sum([item.item_amount for item in items])
    reimbursement.total_amount = decimal.Decimal(total)
    reimbursement.save()


# ============================================================
# =============== CUSTOM EXPORT FUNCTIONS ====================
# ============================================================

def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=reimbursements.csv'
    writer = csv.writer(response)

    writer.writerow(["ID", "User", "Title", "Total", "Status", "Created"])
    for r in queryset:
        writer.writerow([r.id, r.user.username, r.title, r.total_amount, r.status, r.created_at])

    return response

export_as_csv.short_description = "Export CSV"


def export_as_excel(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.append(["ID", "User", "Title", "Total", "Status", "Created"])

    for r in queryset:
        ws.append([r.id, r.user.username, r.title, r.total_amount, r.status, r.created_at])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=reimbursements.xlsx'
    wb.save(response)

    return response

export_as_excel.short_description = "Export Excel"


# ============================================================
# ================== REIMBURSEMENT ADMIN =====================
# ============================================================

@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('title', 'user__username')
    autocomplete_fields = ['user']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("User Info", {'fields': ('user',)}),
        ("Reimbursement Details", {
            'fields': ('title', 'description', 'total_amount', 'status', 'image'),
        }),
        ("Timestamps", {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    inlines = [ReimbursementItemsInline]

    # Custom admin actions
    actions = ['approve_reimbursement', 'reject_reimbursement', export_as_csv, export_as_excel]

    def save_formset(self, request, form, formset, change):
        """Update total automatically when items change."""
        instances = formset.save(commit=False)
        for obj in instances:
            obj.save()

        formset.save_m2m()

        update_total_amount(form.instance)

    def approve_reimbursement(self, request, queryset):
        updated = queryset.update(status='Approved')
        self.message_user(request, f"{updated} reimbursement(s) approved.", messages.SUCCESS)

    def reject_reimbursement(self, request, queryset):
        updated = queryset.update(status='Rejected')
        self.message_user(request, f"{updated} reimbursement(s) rejected.", messages.WARNING)


# ============================================================
# ====================== CATEGORY ADMIN ======================
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


# ============================================================
# ==================== ITEMS ADMIN ===========================
# ============================================================

@admin.register(ReimbursementItems)
class ReimbursementItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'reimbursement', 'category', 'item_amount', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('reimbursement__title', 'category__name')
    autocomplete_fields = ['reimbursement', 'category']
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        """Update total amount whenever item changes."""
        super().save_model(request, obj, form, change)
        update_total_amount(obj.reimbursement)


# ============================================================
# ================= FINANCE MANAGEMENT ADMIN =================
# ============================================================

@admin.register(FinanceManagement)
class FinanceManagementAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'base_salary', 'spouse_allowance', 'child_allowance',
        'bpjs_health_percentage', 'bpjs_employment_percentage',
        'tax_amount', 'overtime_hours', 'receivable_amount', 'created_at'
    )
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)
    autocomplete_fields = ['user']
    readonly_fields = ('created_at', 'updated_at', 'gross_salary', 'net_salary')

    fieldsets = (
        ("User Info", {'fields': ('user',)}),
        ("Salary & Allowances", {
            'fields': ('base_salary', 'spouse_allowance', 'child_allowance'),
        }),
        ("BPJS Deductions", {
            'fields': ('bpjs_health_percentage', 'bpjs_employment_percentage'),
        }),
        ("Other Financial Info", {
            'fields': ('tax_amount', 'overtime_hours', 'receivable_amount'),
        }),
        ("Salaries", {
            'fields': ('gross_salary', 'net_salary'),
        }),
        ("Timestamps", {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
