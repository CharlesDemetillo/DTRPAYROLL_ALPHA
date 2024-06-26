from django.contrib import admin
from .models import Employee, Department, Position, DTR, LoansTaxes, Deductions, Benefits

class DeductionsInline(admin.TabularInline):
    model = Deductions

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    inlines = [DeductionsInline]

admin.site.register(Department)
admin.site.register(Position)
admin.site.register(DTR)
admin.site.register(LoansTaxes)
admin.site.register(Deductions)
admin.site.register(Benefits)