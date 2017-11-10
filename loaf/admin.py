from django.contrib import admin

from loaf.models import Question, Choice

# admin.StackedInline  admin.TabularInline
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1

# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    ''' 定义编辑页面样式 '''
#     fields = ['publish_date', 'question_text']
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['publish_date'],
                              'classes': ['collapse']}),
        ]
    inlines = [ChoiceInline]
    
    ''' 显示字段  还可以把方法作为字段'''
    list_display = ('question_text', 'publish_date', 'was_published_recently')
    ''' 添加某字段过滤器 '''
    list_filter = ['question_text', 'publish_date']
    ''' 添加某字段搜索 '''
    search_fields = ['question_text', 'publish_date']
    
    
admin.site.register(Question, QuestionAdmin)