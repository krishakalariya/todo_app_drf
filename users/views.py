from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView

from .serializers import UserSerializer, LoginSerializer, LogoutSerializer
from .models import User
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .utils import get_tokens_for_user


class RegisterAPI(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(response_data)


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        serializers = LoginSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist as e:
            raise ValidationError('NO_USER_FOUND') from e
        if not check_password(password, user.password):
            raise ValidationError('INVALID_CREDENTIALS')
        data = get_tokens_for_user(user)

        return Response(data, status=status.HTTP_200_OK)


class LogoutView(TokenBlacklistView):
    """
    View for logout user
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
