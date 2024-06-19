from django.contrib import admin

# Register your models here.

from .models import Category, BudgetCategoryMonthlyLimit, Transaction

admin.site.register(Category)
admin.site.register(BudgetCategoryMonthlyLimit)
admin.site.register(Transaction)