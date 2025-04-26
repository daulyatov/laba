from django.contrib import admin
from .models import Incident, DetectedFace

class DetectedFaceInline(admin.TabularInline):
    model = DetectedFace
    extra = 0
    readonly_fields = ('timestamp', 'created_at')

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'faces_found', 'created_at', 'processed_at')
    list_filter = ('status', 'faces_found')
    search_fields = ('name',)
    readonly_fields = ('status', 'processed_at', 'faces_found')
    inlines = [DetectedFaceInline]

@admin.register(DetectedFace)
class DetectedFaceAdmin(admin.ModelAdmin):
    list_display = ('incident', 'timestamp', 'created_at')
    list_filter = ('incident',)
    search_fields = ('incident__name',)
    readonly_fields = ('timestamp', 'created_at') 