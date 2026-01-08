from django.urls import path
from .views import (
    ApplicationListView, ApplicationCreateView, ApplicationUpdateView, ApplicationDeleteView,
    ApplicationDetailView, ApplicationStartSessionView, ApplicationGenerateTokenView,
    ApplicationGetQRCodeView, ApplicationCheckStatusView, ApplicationGetPhoneNumberView,
    ApplicationCloseSessionView, ApplicationRestartSessionView, ApplicationCheckConnectionView,
    ApplicationSyncContactsView, ApplicationSyncMessagesView, WebhookView,
    ConfigListView, ConfigCreateView, ConfigUpdateView, ConfigDeleteView,
    ConversationListView, ConversationDetailView,
    SendMessageView, SendFileView, SendMenuSelectView
)

urlpatterns = [
    # Application URLs
    path('applications/', ApplicationListView.as_view(), name='application-list'),
    path('applications/create/', ApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/update/', ApplicationUpdateView.as_view(), name='application-update'),
    path('applications/<int:pk>/delete/', ApplicationDeleteView.as_view(), name='application-delete'),
    
    # Application Actions
    path('applications/<int:pk>/generate-token/', ApplicationGenerateTokenView.as_view(), name='application-generate-token'),
    path('applications/<int:pk>/start-session/', ApplicationStartSessionView.as_view(), name='application-start-session'),
    path('applications/<int:pk>/get-qr-code/', ApplicationGetQRCodeView.as_view(), name='application-get-qr-code'),
    path('applications/<int:pk>/check-status/', ApplicationCheckStatusView.as_view(), name='application-check-status'),
    path('applications/<int:pk>/get-phone-number/', ApplicationGetPhoneNumberView.as_view(), name='application-get-phone-number'),
    path('applications/<int:pk>/close-session/', ApplicationCloseSessionView.as_view(), name='application-close-session'),
    path('applications/<int:pk>/restart-session/', ApplicationRestartSessionView.as_view(), name='application-restart-session'),
    path('applications/<int:pk>/check-connection/', ApplicationCheckConnectionView.as_view(), name='application-check-connection'),
    path('applications/<int:pk>/sync-contacts/', ApplicationSyncContactsView.as_view(), name='application-sync-contacts'),
    path('applications/<int:pk>/sync-messages/', ApplicationSyncMessagesView.as_view(), name='application-sync-messages'),
    
    # Webhooks
    path('webhook/<str:webhook_key>/', WebhookView.as_view(), name='webhook'),

    # Configuration URLs
    path('configs/', ConfigListView.as_view(), name='config-list'),
    path('configs/create/', ConfigCreateView.as_view(), name='config-create'),
    path('configs/<int:pk>/update/', ConfigUpdateView.as_view(), name='config-update'),
    path('configs/<int:pk>/delete/', ConfigDeleteView.as_view(), name='config-delete'),

    # Conversation URLs
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),

    # Messaging APIs
    path('send-message/', SendMessageView.as_view(), name='send_message'),
    path('send-file/', SendFileView.as_view(), name='send_file'),
    path('send-list-message/', SendMenuSelectView.as_view(), name='send_list_message'),
]
