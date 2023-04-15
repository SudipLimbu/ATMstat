from django.contrib import admin

from transactions.models import Transaction, EOD
from django.contrib import admin


class EODAdmin(admin.ModelAdmin):
    list_display = ("account", "EOD_figure", "tranx_date")


admin.site.register(EOD, EODAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "amount", "balance_after_transaction")


admin.site.register(Transaction, TransactionAdmin)
