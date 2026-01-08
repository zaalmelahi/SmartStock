from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Application, ApplicationConfiguration, Conversation, Message, Template, UserPreferences


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False
    ordering = ('created_at',)


class ConversationAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user_identifier', 'application', 'updated_at', 'started_at')
    list_filter = ('application', 'updated_at')
    search_fields = ('session_id', 'user_identifier')
    inlines = [MessageInline]
    readonly_fields = ('started_at', 'updated_at')


class ApplicationConfigurationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the ApplicationConfiguration model.
    """
    list_display = ('name', 'botpress_url', 'flow_ai', 'use_voice_message', 'use_accounting_agent', 'created_at')
    list_filter = ('flow_ai', 'use_voice_message', 'use_accounting_agent')
    search_fields = ('name', 'botpress_url', 'flow_id')
    
    fieldsets = [
        (_("Basic Information"), {
            'fields': ('name',),
        }),
        (_("BotPlatform Configuration"), {
            'fields': (
                'botpress_url',
                'botpress_username',
                'botpress_password',
                'botpress_token',
                'token_expires_at',
            ),
        }),
        (_("System Configuration"), {
            'fields': (
                'system_url',
                'system_auth_info',
                'url',
                'token',
            ),
        }),
        (_("Feature Flags"), {
            'fields': (
                'use_voice_message',
                'url_voice',
                'use_accounting_agent',
                'flow_ai',
            ),
        }),
        (_("Flow AI Configuration"), {
            'fields': (
                'flow_id',
                'flow_token',
            ),
            'classes': ('collapse',),
        }),
    ]


class ApplicationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Application model.
    """
    list_display = (
        'name', 'whatsapp_provider_type', 'enabled', 'phone'
    )
    list_filter = (
        'whatsapp_provider_type',
        'enabled',
        'auto_replay_group',
        'apply_authorized_contact',
    )
    search_fields = ('name', 'phone', 'webhook_key', 'bot_id')
    
    fieldsets = [
        (_("Basic Information"), {
            'fields': (
                ('auto_replay_group', "enabled", "apply_authorized_contact"),
                ('name', 'configuration'),
            ),
        }),
        (_("Bot Configuration"), {
            'fields': (
                ('bot_id', 'app_id'),
            ),
        }),
        (_("WhatsApp Settings"), {
            'fields': (
                ('webhook_key', 'whatsapp_provider_type', 'session'),
                ('phone',),
            ),
        }),
    ]


class UserPreferencesAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserPreferences model.
    """
    list_display = ('phone_number', 'preferred_format', 'max_items_per_page', 'language', 'updated_at')
    list_filter = ('preferred_format', 'language', 'updated_at')
    search_fields = ('phone_number',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = [
        (_("User Information"), {
            'fields': ('phone_number',),
        }),
        (_("Display Preferences"), {
            'fields': (
                'preferred_format',
                'max_items_per_page',
                'language',
            ),
        }),
        (_("Timestamps"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]


admin.site.register(ApplicationConfiguration, ApplicationConfigurationAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message)
admin.site.register(Template)
admin.site.register(UserPreferences, UserPreferencesAdmin)
