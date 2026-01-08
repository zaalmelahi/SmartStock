from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from ..models import Application
from ..forms import ApplicationForm

class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'integration/application_list.html'
    context_object_name = 'applications'
    paginate_by = 10

class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'integration/application_form.html'
    success_url = reverse_lazy('application-list')

class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'integration/application_form.html'
    success_url = reverse_lazy('application-list')

class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = 'integration/application_confirm_delete.html'
    success_url = reverse_lazy('application-list')

class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = 'integration/application_detail.html'
    context_object_name = 'application'
