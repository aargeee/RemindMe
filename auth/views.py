"""Reminder app views."""

from __future__ import annotations

import typing
from typing import TYPE_CHECKING

from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.serializers import UserSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class SignupView(APIView):
    """Signup view for RemindMe API."""

    permission_classes: typing.ClassVar = [AllowAny]

    def post(self: SignupView, request: Request) -> Response:
        """Signup."""
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "data": {
                        "errors": serializer.errors,
                    },
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        password: str = request.data["password"]
        validate_password(password=password)
        User.objects.create_user(
            username=request.data["username"],
            password=request.data["password"],
        )
        return Response(
            {
                "success": True,
                "data": {
                    "detail": "User Created.",
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Login."""

    def post(self: LoginView, request: Request) -> Response:
        """Login."""
        username = request.data.get("username")
        password = request.data.get("password")

        if not (username and password):
            return Response(
                {
                    "success": False,
                    "data": {"detail": "Username or password is missing."},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=username).first()

        if not user or not user.check_password(password):
            return Response(
                {"success": False, "data": {"detail": "Invalid username or password."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response({"success": True, "data": {"token": token.key}})


class LogoutView(APIView):
    """Logout."""

    permission_classe: typing.ClassVar = [IsAuthenticated]

    def post(self: LogoutView, request: Request) -> Response:
        """Logout."""
        user: User = request.user
        if type(user) is AnonymousUser:
            return Response(
                {"detail": "Authentication credentials required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user_token: Token = user.auth_token
        user_token.delete()
        return Response({"detail": "Logout Successful"}, status=status.HTTP_200_OK)
