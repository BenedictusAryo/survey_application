from django.contrib import admin
from .models import Response, ResponseAnswer

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'form', 'user', 'is_complete', 'submitted_at')
    list_filter = ('is_complete', 'submitted_at', 'form')
    search_fields = ('form__title', 'user__username')
    readonly_fields = ('submitted_at', 'updated_at')

@admin.register(ResponseAnswer)
class ResponseAnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'value', 'created_at')
    list_filter = ('created_at', 'question__question_type')
    search_fields = ('response__form__title', 'question__text')
