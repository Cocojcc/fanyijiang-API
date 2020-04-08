from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# Create your models here.

class ReadNums(models.Model):
    nums = models.IntegerField(default=0, verbose_name='总阅读量')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100, verbose_name='对象ID')
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'read_nums'
