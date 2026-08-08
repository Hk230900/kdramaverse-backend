from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer

User = get_user_model()


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from datetime import timedelta

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # We need to manually check if user exists and is inactive for restoration
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
            if not user.is_active and user.deletion_requested_at:
                # Check if within 48 hours
                if timezone.now() < user.deletion_requested_at + timedelta(hours=48):
                    # Check password before restoring
                    if user.check_password(password):
                        # Restore account!
                        user.is_active = True
                        user.deletion_requested_at = None
                        user.save()
                    else:
                        raise serializers.ValidationError('No active account found with the given credentials')
                else:
                    # Over 48 hours! Permanently delete the user right now.
                    user.delete()
                    raise serializers.ValidationError('Account permanently deleted. You can create a new one.')
        except User.DoesNotExist:
            pass
            
        return super().validate(attrs)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Intercept to check for expired deleted accounts taking up the email
        email = request.data.get('email')
        if email:
            try:
                existing_user = User.objects.get(email=email)
                if not existing_user.is_active and existing_user.deletion_requested_at:
                    if timezone.now() >= existing_user.deletion_requested_at + timedelta(hours=48):
                        existing_user.delete()
            except User.DoesNotExist:
                pass

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Account created successfully.',
            'user': UserSerializer(user, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_context(self):
        return {'request': self.request}


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.deletion_requested_at = timezone.now()
        user.save()
        return Response({'message': 'Account marked for deletion. It will be permanently removed in 48 hours.'})


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            return Response({'security_question': user.security_question})
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        security_answer = request.data.get('security_answer')
        new_password = request.data.get('new_password')

        if not all([email, security_answer, new_password]):
            return Response({'error': 'Email, security answer, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.security_answer.lower().strip() != security_answer.lower().strip():
            return Response({'error': 'Incorrect security answer'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic validation (can use django validators here, but keeping it simple)
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successful. You can now log in.'})
