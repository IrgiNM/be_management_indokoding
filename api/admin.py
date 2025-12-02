import csv
import decimal
from datetime import datetime

from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from openpyxl import Workbook
from unfold.admin import ModelAdmin
from unfold.admin import TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import (
    Reimbursement, Category, ReimbursementItems, FinanceManagement, SalarySlip, Employee, BankAccount, SiteSetting,
    OvertimeLog, UserOvertimeLog
)

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(SiteSetting)
class SiteSettingAdmin(ModelAdmin):
    list_display = ("category", "key", "value", "updated_at")
    list_filter = ("category",)
    search_fields = ("category", "key", "value")
    ordering = ("category", "key")


class BankAccountInline(TabularInline):
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
class EmployeeAdmin(ModelAdmin):
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

class ReimbursementItemsInline(TabularInline):
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
class ReimbursementAdmin(ModelAdmin):
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
class CategoryAdmin(ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)



# ============================================================
# ================= FINANCE MANAGEMENT ADMIN =================
# ============================================================

@admin.register(FinanceManagement)
class FinanceManagementAdmin(ModelAdmin):
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
class OvertimeLogAdmin(ModelAdmin):
    list_display = (
        "user",
        "date",
        "paid_date",
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
            "fields": ("status", "paid_date")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        # Non-admin cannot change status or paid_date
        if obj and obj.status == "approved":
            ro_fields = [f.name for f in obj._meta.fields]
            if request.user.is_superuser:
                ro_fields.remove("paid_date")
            return ro_fields

        return ro_fields
    # ACTIONS
    actions = ["approve_logs", "reject_logs"]

    def approve_logs(self, request, queryset):
        updated = queryset.update(status="approved", paid_date=datetime.now())
        self.message_user(request, f"{updated} overtime logs approved.")

    approve_logs.short_description = "Approve selected overtime logs"

    def reject_logs(self, request, queryset):
        updated = queryset.update(status="rejected", paid_date=None)
        self.message_user(request, f"{updated} overtime logs rejected.")

    reject_logs.short_description = "Reject selected overtime logs"

    def has_delete_permission(self, request, obj=None):
        # Superuser can delete anything
        if request.user.is_superuser:
            return True

        # If editing a specific object
        if obj:
            # Prevent deleting approved logs
            if obj.status == "approved":
                return False

        # Allow delete for other statuses
        return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        print("ACTIONS : ", actions)
        # Remove bulk delete action for non-superusers
        if not request.user.is_superuser:
            if "delete_selected" in actions:
                del actions["delete_selected"]
        return actions

@admin.register(UserOvertimeLog)
class UserOvertimeLogAdmin(OvertimeLogAdmin):
    list_filter = ("status", "date")
    list_display = (
        "date",
        "paid_date",
        "start_time",
        "end_time",
        "duration_hours",
        "status",
        "created_at",
    )
    readonly_fields = ("status", "paid_date", "duration_hours", "created_at", "updated_at")

    actions = []
    fieldsets = (
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
            "fields": ("status", "paid_date")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    # Make sure logged-in user sees ONLY their own overtime logs
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user=request.user)

    # Automatically assign the logged-in user on save
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set user for new records
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(SalarySlip)
class SalarySlipAdmin(ModelAdmin):
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

    readonly_fields = (
        "finance",
        "user",
        "month",
        "year",
        "gross_salary",
        "bpjs_health",
        "bpjs_employment",
        "tax_amount",
        "overtime_pay",
        "net_salary",
        "created_at"
    )

    fieldsets = (
        ("Employee", {
            "fields": ("user",)
        }),
        ("Deductions", {
            "fields": (
                "bpjs_health",
                "bpjs_employment",
                "tax_amount",
            )
        }),
        ("Additional", {
            "fields": ("overtime_pay",)
        }),
        ("Salaries", {
            "fields": ("net_salary",)
        }),
        ("Timestamps", {
            "fields": ("month", "year", "created_at")
        }),
    )

    actions = ["generate_monthly_slip"]

    def has_add_permission(self, request):
        return False

    def generate_monthly_slip(self, request, queryset):
        """
        Membuat slip gaji untuk seluruh karyawan pada bulan & tahun tertentu.
        """
        now = datetime.now()
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