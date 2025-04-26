from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Incident, DetectedFace
from .serializers import IncidentSerializer, DetectedFaceSerializer
import cv2
import os
from django.conf import settings
from django.core.files.storage import default_storage
import threading
from django.utils import timezone

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer

    @action(detail=True, methods=['post'])
    def process_video(self, request, pk=None):
        incident = self.get_object()
        if incident.status != 'pending':
            return Response({'error': 'Video is already being processed or processed'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        incident.status = 'processing'
        incident.save()
        
        # Start processing in background
        threading.Thread(target=self._process_video, args=(incident,)).start()
        
        return Response({'status': 'Processing started'})

    def _process_video(self, incident):
        try:
            video_path = incident.video_file.path
            cap = cv2.VideoCapture(video_path)
            
            # Load the face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            frame_count = 0
            faces_found = False
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 10th frame to save resources
                if frame_count % 10 == 0:
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )
                    
                    if len(faces) > 0:
                        faces_found = True
                        for (x, y, w, h) in faces:
                            face_image = frame[y:y+h, x:x+w]
                            
                            # Save face image
                            face_filename = f'face_{incident.id}_{frame_count}.jpg'
                            face_path = os.path.join(settings.MEDIA_ROOT, 'faces', face_filename)
                            cv2.imwrite(face_path, face_image)
                            
                            # Create DetectedFace instance
                            DetectedFace.objects.create(
                                incident=incident,
                                face_image=f'faces/{face_filename}',
                                timestamp=frame_count / cap.get(cv2.CAP_PROP_FPS)
                            )
                
                frame_count += 1
            
            cap.release()
            
            incident.status = 'completed'
            incident.faces_found = faces_found
            incident.processed_at = timezone.now()
            incident.save()
            
        except Exception as e:
            incident.status = 'failed'
            incident.save()
            print(f"Error processing video: {str(e)}")

def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        video_file = request.FILES.get('video')
        if name and video_file:
            Incident.objects.create(name=name, video_file=video_file)
    
    incidents = Incident.objects.all().order_by('-created_at')
    return render(request, 'incidents/home.html', {'incidents': incidents})

def incident_detail(request, pk):
    incident = get_object_or_404(Incident, pk=pk)
    
    if request.method == 'POST':
        if incident.status == 'pending':
            incident.status = 'processing'
            incident.save()
            threading.Thread(target=IncidentViewSet._process_video, args=(None, incident)).start()
    
    return render(request, 'incidents/incident_detail.html', {'incident': incident}) 