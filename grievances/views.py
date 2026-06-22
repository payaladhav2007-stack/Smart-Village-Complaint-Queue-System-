from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Complaint
from .serializers import ComplaintSerializer


class SubmitComplaintView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        media_file = request.data.get('media_path')
        serializer = ComplaintSerializer(data=request.data)

        if serializer.is_valid():
            # Save first without the file so the complaint gets a real id
            complaint = serializer.save(user=request.user, media_path=None)

            # Now attach the file (if provided) — id exists, so upload_to resolves correctly
            if media_file:
                complaint.media_path = media_file
                complaint.save()

            return Response({
                "message": "Grievance submitted successfully.",
                "complaint": {
                    "id": complaint.id,
                    "category": complaint.category,
                    "description": complaint.description,
                    "status": complaint.status,
                    "latitude": str(complaint.latitude),
                    "longitude": str(complaint.longitude),
                    "media_path": complaint.media_path.url if complaint.media_path else None,
                    "created_at": str(complaint.created_at)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)