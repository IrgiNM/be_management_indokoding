import csv
import datetime
import decimal

from django.contrib import admin, messages
from django.http import HttpResponse
from openpyxl import Workbook

from .models import (
    Reimbursement, Category, ReimbursementItems, FinanceManagement, SalarySlip, Employee, BankAccount, SiteSetting,
    OvertimeLog
)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("category", "key", "value", "updated_at")
    list_filter = ("category",)
    search_fields = ("category", "key", "value")
    ordering = ("category", "key")

class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 1
    fields = (
        "bank_name",
        "account_number",
        "account_holder",
        "is_primary",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "full_name",
        "department",
        "position",
        "employment_status",
        "join_date",
    )
    list_filter = ("department", "employment_status", "gender")
    search_fields = ("employee_id", "full_name", "user__username")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("full_name",)

    inlines = [BankAccountInline]

    fieldsets = (
        ("Account", {
            "fields": ("user", "employee_id")
        }),
        ("Personal Info", {
            "fields": ("full_name", "gender", "birth_date", "address", "phone_number", "email", "identity_number", "tax_number")
        }),
        ("Job Info", {
            "fields": ("department", "position", "employment_status", "join_date", "resign_date")
        }),
        ("Emergency Contact", {
            "fields": ("emergency_name", "emergency_phone", "emergency_relation")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
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
# ================= FINANCE MANAGEMENT ADMIN =================
# ============================================================

@admin.register(FinanceManagement)
class FinanceManagementAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'is_active', 'user', 'base_salary', 'spouse_allowance', 'child_allowance', 'enable_bpjs_health',
        'bpjs_health_rate_percentage', 'enable_bpjs_employment', 'bpjs_employment_rate_percentage', 'enable_tax',
        'tax_rate_percentage', 'created_at'
    )
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)
    autocomplete_fields = ['user']
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("User Info", {'fields': ('is_active', 'user',)}),
        ("Salary & Allowances", {
            'fields': ('base_salary', 'spouse_allowance', 'child_allowance'),
        }),
        ("BPJS Deductions", {
            'fields': ('enable_bpjs_health', 'bpjs_health_rate_percentage', 'enable_bpjs_employment', 'bpjs_employment_rate_percentage'),
        }),
        ("Other Financial Info", {
            'fields': ('enable_tax', 'tax_rate_percentage'),
        }),
        ("Timestamps", {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(OvertimeLog)
class OvertimeLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "date",
        "start_time",
        "end_time",
        "duration_hours",
        "status",
        "created_at",
    )
    list_filter = ("status", "date", "user")
    search_fields = ("user__username", "user__first_name", "user__last_name", "description")
    readonly_fields = ("duration_hours", "created_at", "updated_at")
    ordering = ("-date", "-created_at")

    fieldsets = (
        ("Employee", {
            "fields": ("user",)
        }),
        ("Overtime Details", {
            "fields": (
                "date",
                "start_time",
                "end_time",
                "duration_hours",
                "description",
            )
        }),
        ("Workflow", {
            "fields": ("status",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # ACTIONS
    actions = ["approve_logs", "reject_logs"]

    def approve_logs(self, request, queryset):
        updated = queryset.update(status="approved")
        self.message_user(request, f"{updated} overtime logs approved.")

    approve_logs.short_description = "Approve selected overtime logs"

    def reject_logs(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} overtime logs rejected.")

    reject_logs.short_description = "Reject selected overtime logs"


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "month",
        "year",
        "gross_salary",
        "net_salary",
        "created_at",
    )
    list_filter = ("year", "month", "user")
    search_fields = ("user__username",)

    actions = ["generate_monthly_slip"]

    def generate_monthly_slip(self, request, queryset):
        """
        Membuat slip gaji untuk seluruh karyawan pada bulan & tahun tertentu.
        """
        now = datetime.datetime.now()
        year = request.GET.get("year", now.year)
        month = request.GET.get("month", now.month)

        employees = FinanceManagement.objects.select_related("user")

        created = 0
        skipped = 0

        for finance in employees:
            obj, created_flag = SalarySlip.objects.get_or_create(
                user=finance.user,
                finance=finance,
                year=year,
                month=month,
            )
            if created_flag:
                created += 1
            else:
                skipped += 1

        self.message_user(request, f"{created} slip dibuat, {skipped} dilewati (sudah ada).")

    generate_monthly_slip.short_description = "Generate Slip Gaji Bulanan"