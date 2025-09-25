from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from apps.commerce.models.invoice import Invoice
from apps.commerce.models.invoice_detail import InvoiceDetail


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'pages/settings/invoice/list/page.html'
    context_object_name = 'invoices'
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invoice List'
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'pages/settings/invoice/detail/page.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invoice Detail'
        context['details'] = InvoiceDetail.objects.filter(invoice=self.object)
        return context
