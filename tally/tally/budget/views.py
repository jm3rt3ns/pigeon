from django.shortcuts import render
from django.views.generic.edit import CreateView

from .forms import TransactionForm
from .models import Category
from django.shortcuts import get_object_or_404

# 3rd party
from datetime import datetime

# Create your views here.
def view_budget(request):
    print("VIEWING BUDGET")
    print(request.method)
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'budget/view_budget.html', { "categories": Category.objects.all() })
        else:
            print(form.errors)

    return render(request, 'budget/view_budget.html', { "categories": Category.objects.all() })

def remaining_budget(request):
    # get the category id from the request query param
    category_id = request.GET.get('category')
    # get the category object
    category = get_object_or_404(Category, pk=category_id)
    # get the transactions for the category, filtered to the current month
    month = datetime.now().month
    print("month", month, category.name)
    transactions = category.transaction_set.filter(date__month=month)
    print(transactions)

    # calculate the total spent for the month
    total_spent = sum([transaction.value for transaction in transactions])

    # get the budget limit for the category
    budget_limit = category.budgetcategorymonthlylimit_set.get().limit

    # calculate the remaining budget
    remaining_budget = budget_limit - total_spent

    return render(request, 'budget/remaining_budget.html', { "category": category, "remaining_budget": remaining_budget })

class AuthorCreateView(CreateView):
    form_class = TransactionForm
    template_name = 'budget/view_budget.html'
    success_url = 'success'
