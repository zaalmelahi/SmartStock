from django.db import models
from django.utils.translation import gettext_lazy as _

class PendingOperation(models.Model):
    """
    Stores partial state for multi-step operations like creating a 
    purchase order or sale. This allows the agent to 'remember' 
    previously provided information across multiple messages.
    """
    
    OPERATION_CHOICES = [
        ('purchase_order', _('Purchase Order')),
        ('sale', _('Sale')),
        ('create_customer', _('Create Customer')),
    ]
    
    phone_number = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        verbose_name=_('Phone Number')
    )
    
    operation_type = models.CharField(
        max_length=50, 
        choices=OPERATION_CHOICES,
        verbose_name=_('Operation Type')
    )
    
    data = models.JSONField(
        default=dict,
        verbose_name=_('Collected Data'),
        help_text=_('JSON data storing partial information for the operation')
    )
    
    step = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('Current Step')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Pending Operation')
        verbose_name_plural = _('Pending Operations')
        
    def __str__(self):
        return f"{self.phone_number} - {self.operation_type}"
