from django.db import models
from django.conf import settings

# Create your models here.
class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'Search Histories'

    def __str__(self):
        return f"{self.user.username} searched: {self.query}"
