from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from .models import Feedback
from .serializers import FeedbackSubmitSerializer


class SubmitFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackSubmitSerializer(data=request.data)
        if serializer.is_valid():
            target = serializer.validated_data.get('_target')
            model = serializer.validated_data.get('_model')

            if target is None:
                return Response(
                    {"message": "Feedback submitted successfully."},
                    status=status.HTTP_201_CREATED
                )

            content_type = ContentType.objects.get_for_model(model)

            # Check duplicate
            if Feedback.objects.filter(
                content_type=content_type,
                target_object_id=target.id,
                submitted_by=request.user
            ).exists():
                return Response(
                    {"error": "You have already submitted feedback for this ticket."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create feedback
            Feedback.objects.create(
                content_type=content_type,
                target_object_id=target.id,
                submitted_by=request.user,
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data.get('comment', '')
            )

            return Response(
                {"message": "Feedback submitted successfully."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def feedback_form(request):
    return render(request, 'feedback/feedback_form.html')
