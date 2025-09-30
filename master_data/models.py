from django.db import models
from django.conf import settings as django_settings

class MasterDataSet(models.Model):
    """Master data set containing reusable demographic/reference data"""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_datasets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Sharing settings
    shared_with = models.ManyToManyField(
        django_settings.AUTH_USER_MODEL, 
        through='MasterDataSetShare',
        related_name='shared_datasets'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class MasterDataSetShare(models.Model):
    """Sharing relationship between datasets and users"""
    
    dataset = models.ForeignKey(MasterDataSet, on_delete=models.CASCADE)
    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    can_edit = models.BooleanField(default=False)  # View-only by default
    shared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['dataset', 'user']


class MasterDataColumn(models.Model):
    """Column definition for master data sets"""
    
    DATA_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('email', 'Email'),
    ]
    
    dataset = models.ForeignKey(MasterDataSet, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES, default='text')
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['dataset', 'name']
    
    def __str__(self):
        return f"{self.dataset.name} - {self.name}"


class MasterDataRecord(models.Model):
    """Individual record within a master data set"""
    
    dataset = models.ForeignKey(MasterDataSet, on_delete=models.CASCADE, related_name='records')
    data = models.JSONField(default=dict)  # Flexible data storage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        # Try to show the first text field as identifier
        name_field = None
        for column in self.dataset.columns.all():
            if 'nama' in column.name.lower() or 'name' in column.name.lower():
                name_field = column.name
                break
        
        if name_field and name_field in self.data:
            return f"{self.dataset.name} - {self.data[name_field]}"
        return f"{self.dataset.name} - Record #{self.id}"
