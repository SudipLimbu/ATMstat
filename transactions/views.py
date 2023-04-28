from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView

from transactions.constants import DEPOSIT, WITHDRAWAL
from transactions.forms import (
    DepositForm,
    TransactionDateRangeForm,
    WithdrawForm,
)
from transactions.models import Transaction, EOD

from django.db.models import Sum  # to add the total EOD figure

# For forecast
import pandas as pd
from prophet import Prophet
import joblib

from django.shortcuts import render


class EODView(LoginRequiredMixin, ListView):
    template_name = 'transactions/EOD.html'
    model = EOD
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(tranx_date__range=daterange)
        else:
            # Get the last 30 records
            queryset = queryset.order_by('-tranx_date')[:30]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate the sum of the last 30 EOD figures
        queryset = self.get_queryset()
        eod_sum = queryset.aggregate(Sum('EOD_figure'))['EOD_figure__sum']

        print("EOD Sum:", eod_sum)  # Add a print statement to debug the sum

        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None),
            'eod_sum': eod_sum,  # Add the sum to the context
        })
        return context

# extract the data


def get_eod_data(account):
    eod_records = EOD.objects.filter(account=account)
    data = pd.DataFrame.from_records(
        eod_records.values('tranx_date', 'EOD_figure'))
    data.columns = ['ds', 'y']
    data['ds'] = pd.to_datetime(data['ds'])

    # Get the last 730 rows of data
    data = data.tail(730)
    return data

#forecast = train_and_save_prophet_model(account, days=7)


def train_and_save_prophet_model(account, days=14):
    data = get_eod_data(account)
    model = Prophet()
    model.fit(data)

    last_date = data['ds'].max()  # Get the last date in the data
    future_dates = pd.date_range(
        start=last_date, periods=days + 1)  # Generate future dates
    future = pd.DataFrame({'ds': future_dates})  # Create a future dataframe

    forecast = model.predict(future)

    joblib.dump(model, f'prophet_model_account_{account.id}.pkl')

    return forecast


class ForecastView(LoginRequiredMixin, ListView):
    def get(self, request):
        account = request.user.account
        # Get the EOD data and train the Prophet model
        forecast = train_and_save_prophet_model(
            account, days=14)  # Pass the days parameter

        # Pass the forecast data to the template
        context = {
            'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient='records'),
        }
        return render(request, 'transactions/forecast.html', context)


class TransactionRepostView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    form_data = {}

    def get(self, request, *args, **kwargs):
        form = TransactionDateRangeForm(request.GET or None)
        if form.is_valid():
            self.form_data = form.cleaned_data

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )

        daterange = self.form_data.get("daterange")

        if daterange:
            queryset = queryset.filter(timestamp__date__range=daterange)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'form': TransactionDateRangeForm(self.request.GET or None)
        })

        return context


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transactions:transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'ATM Replenishment'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    MAX_AMOUNT = 180000  # set the maximum amount allowed

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account

        # check if the amount exceeds the maximum limit
        if amount > self.MAX_AMOUNT:
            form.add_error(
                'amount',
                f'Amount cannot exceed {"{:,.2f}".format(float(self.MAX_AMOUNT))}$'
            )
            return self.form_invalid(form)

        if not account.initial_deposit_date:
            now = timezone.now()
            next_interest_month = int(
                12 / account.account_type.interest_calculation_per_year
            )
            account.initial_deposit_date = now
            account.interest_start_date = (
                now + relativedelta(
                    months=+next_interest_month
                )
            )

        account.balance += amount
        account.save(
            update_fields=[
                'initial_deposit_date',
                'balance',
                'interest_start_date'
            ]
        )

        messages.success(
            self.request,
            f'£{"{:,.2f}".format(float(amount))} was deposited to your ATM successfully'
        )

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Decash'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully Removed -£{"{:,.2f}".format(float(amount))} from your ATM'
        )

        return super().form_valid(form)
