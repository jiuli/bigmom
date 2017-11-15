from _overlapped import NULL
import datetime
from unittest.util import _MAX_LENGTH

from django.db import models
from django.template.defaultfilters import default
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible # for support python2.x
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    publish_date = models.DateTimeField('问题发布时间')
    
    # 
    def __str__(self):
        return self.question_text
    # 最近是否发布过
    def was_published_recently(self):
        return (timezone.now() - datetime.timedelta(days = 1)) <= self.publish_date <= timezone.now()
        ''' 定义该方法在admin后台作为字段显示的样式 '''
    was_published_recently.boolean = True
    was_published_recently.admin_order_filed = 'publish_date'
    was_published_recently.short_description = '最近近是否发布'
    
class Choice(models.Model):
    ''' cascade表示级联操作，就是说，如果主键表中被关联字段更新，
                        外键表中也更新，主键表中的记录被删除，外键表中改行也相应删除'''
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
    
    