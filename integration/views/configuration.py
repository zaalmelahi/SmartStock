from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..models import ApplicationConfiguration
from ..forms import ApplicationConfigurationForm

class ConfigListView(LoginRequiredMixin, ListView):
    model = ApplicationConfiguration
    template_name = 'integration/config_list.html'
    context_object_name = 'configs'
    paginate_by = 10

class ConfigCreateView(LoginRequiredMixin, CreateView):
    model = ApplicationConfiguration
    form_class = ApplicationConfigurationForm
    template_name = 'integration/config_form.html'
    success_url = reverse_lazy('config-list')

class ConfigUpdateView(LoginRequiredMixin, UpdateView):
    model = ApplicationConfiguration
    form_class = ApplicationConfigurationForm
    template_name = 'integration/config_form.html'
    success_url = reverse_lazy('config-list')

class ConfigDeleteView(LoginRequiredMixin, DeleteView):
    model = ApplicationConfiguration
    template_name = 'integration/config_confirm_delete.html'
    success_url = reverse_lazy('config-list')
