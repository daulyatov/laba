from rest_framework import serializers
from .models import Incident, DetectedFace

class DetectedFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedFace
        fields = ['id', 'face_image', 'timestamp', 'created_at']

class IncidentSerializer(serializers.ModelSerializer):
    faces = DetectedFaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Incident
        fields = ['id', 'name', 'video_file', 'status', 'created_at', 
                 'processed_at', 'faces_found', 'faces']
        read_only_fields = ['status', 'processed_at', 'faces_found'] 