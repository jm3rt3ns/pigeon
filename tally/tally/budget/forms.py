from django.forms import ModelForm
from budget.models import Transaction

# Create the form class.
class TransactionForm(ModelForm):
     class Meta:
         model = Transaction
         fields = ["category", "value"]