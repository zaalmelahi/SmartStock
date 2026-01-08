from django.db import models
from django.utils.translation import gettext_lazy as _


class UserPreferences(models.Model):
    """
    Stores user preferences for WhatsApp interactions.
    Linked to user's phone number to remember display format choices.
    """
    
    FORMAT_CHOICES = [
        ('auto', _('تلقائي - يختار النظام الأنسب')),
        ('text', _('نص - عرض نصي بسيط')),
        ('table', _('جدول - جداول منسقة')),
        ('paginated', _('صفحات - عرض بصفحات متعددة')),
        ('summary', _('ملخص - ملخص مختصر فقط')),
    ]
    
    phone_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_('Phone Number'),
        help_text=_('User phone number (WhatsApp)')
    )
    
    preferred_format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='auto',
        verbose_name=_('Preferred Display Format'),
        help_text=_('How the user prefers to receive data')
    )
    
    max_items_per_page = models.IntegerField(
        default=10,
        verbose_name=_('Items Per Page'),
        help_text=_('Maximum number of items to show per message (5-50)')
    )
    
    language = models.CharField(
        max_length=10,
        default='ar',
        verbose_name=_('Language'),
        help_text=_('Preferred language (ar/en)')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('User Preferences')
        verbose_name_plural = _('User Preferences')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.phone_number} - {self.get_preferred_format_display()}"
    
    def clean(self):
        """Validate max_items_per_page range."""
        from django.core.exceptions import ValidationError
        if self.max_items_per_page < 5 or self.max_items_per_page > 50:
            raise ValidationError({
                'max_items_per_page': _('Must be between 5 and 50')
            })
