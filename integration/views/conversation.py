from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from ..models import Conversation

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'integration/conversation_list.html'
    context_object_name = 'conversations'
    paginate_by = 20
    ordering = ['-updated_at']

class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'integration/conversation_detail.html'
    context_object_name = 'conversation'
