import datetime
import json
import re

import jwt
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.models import Group, update_last_login
from django.db import transaction
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.views import View
from drf_spectacular.utils import extend_schema
from jwt import algorithms
from rest_framework import filters, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

# from social_django.models import UserSocialAuth

from ResumeRanker import settings

from user.serializers import (
    UserLoginSerializer,
    UserLogoutSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    ForgetPasswordLinkSerializer,
    UserSignUpSerializer,
    TokenSerializer,
    UserSerializer,
)
from .utils import generate_random_password




User = get_user_model()

class UserSignUpAPI(CreateAPIView):
    """API view for user signup."""

    serializer_class = UserSignUpSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)



# class UserListAPIView(ListAPIView):
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#     permission_classes = [AllowAny]


# class UserDetailApiView(RetrieveUpdateAPIView):
#     """API view for retrieving  user details."""

#     serializer_class = UserRetrieveUpdateSerializer
#     queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]
#     lookup_field = "id"

#     def get_serializer_class(self):
#         return super().get_serializer_class()

#     def get(self, request, id, *args, **kwargs):
#         qs = User.objects.get(id=id)
#         serializer = UserRetrieveUpdateSerializer(instance=qs)
#         return Response(
#             {
#                 "status": status.HTTP_200_OK,
#                 "message": "Success",
#                 "results": serializer.data,
#             }
#         )


class UserLoginAPI(CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer: UserLoginSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend') # this handle the user login and triggred signals


        refresh: RefreshToken = RefreshToken.for_user(user)
        headers = self.get_success_headers(serializer.data)
        update_last_login(None, user)
        return Response(
            {
                **serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            200,
            headers=headers,
        )


class LogoutAPIView(APIView):
    """
    API view for user logout.
    Accepts a refresh token and blacklists it to invalidate future use.
    """

    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            # logout(request, backend='django.contrib.auth.backends.ModelBackend')  # this handle the user login and triggred signals

            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except TokenError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TokenRefreshView(TokenRefreshView):
    """
    Api view for refreshing JWT tokens.
    This view extends the default TokenRefreshView to use a custom serializer.
    It allows users to refresh their access tokens using a valid refresh token.
    """
    serializer_class = TokenSerializer


# class UserProfileListCreateView(ListCreateAPIView):
#     queryset = UserProfile.objects.all()
#     permission_classes = [IsAuthenticated]

#     def get_serializer_class(self):
#         if self.request.method == "GET":
#             return UserProfileListSerializer
#         return UserProfileCreateSerializer


# class UserProfileRetrieveUpdateView(RetrieveUpdateAPIView):
#     queryset = UserProfile.objects.all()
#     lookup_field = "id"
#     permission_classes = [IsAuthenticated]

#     def get_serializer_class(self):
#         if self.request.method == "GET":
#             return UserProfileRetrieveSerializer
#         return UserProfileRetrieveUpdateSerializer
# ---------------------------------------------------------
# Change Password API
#
# This API is used to change the password for both:
#   1. Regular Account Users
#   2. Socially linked Users
#
# Rules:
# - For Account Users:
#     • `social_token` must be provided.
#
# - For Social Users:
#     • `social_token` is required.
#     • `old_password` should be set to null.
#     • After successful password set, `social_only` is updated to False.
#
# ---------------------------------------------------------


@extend_schema(summary="Change or set password.")
class PasswordChangeAPI(CreateAPIView):


    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user: User = request.user  # type: ignore
            user.set_password(serializer.validated_data["new_password"])
            user.password_changed_date = datetime.datetime.now()
            if not user.is_verified:
                user.is_verified = True
            # try:
            #     social = UserSocialAuth.objects.get(user=user)
            #     user.social_only = False
            # except UserSocialAuth.DoesNotExist:
            #     pass
            user.save()
            return Response({"message": "Password successfully changed"})


@extend_schema(summary="Send reset link to change password")
class PasswordResetAPI(CreateAPIView):
    """
    Password reset view with email
    ------------------------
    # Please use only one: email
    -------------------------
    """

    serializer_class = ForgetPasswordLinkSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        if request.data.get("email"):
            return Response(
                {
                    "status": "success",
                    "message": "Reset link has been sent to your email.",
                }
            )
        else:
            return Response(
                {
                    "status": "success",
                    "message": "An OTP has been sent to your  number.",
                }
            )


class PasswordResetConfirmTemplateView(View):
    template_name = "user/password_reset_confirm.html"

    def get(self, request, *args, **kwargs):
        uid = request.GET.get("u")
        token = request.GET.get("t")
        return render(request, self.template_name, {"uid": uid, "token": token})

    def post(self, request):
        data = {
            "uid": request.POST.get("uid"),
            "token": request.POST.get("token"),
            "new_password": request.POST.get("new_password"),
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return render(
                request,
                self.template_name,
                {"success": "Password has been successfully reset!"},
            )
        else:
            error = next(iter(serializer.errors.values()))[0]
            return render(
                request,
                self.template_name,
                {
                    "uid": data["uid"],
                    "token": data["token"],
                    "error": error,
                },
            )


# class SocialLoginAPI(APIView):
#     permission_classes = [AllowAny]

#     @transaction.atomic
#     def post(self, request, backend, *args, **kwargs):
#         method = getattr(self, f"social_{backend}".replace("-", "_"), None)
#         if not method:
#             return Response(
#                 {"message": f"Unsupported backend '{backend}'."}, status=400
#             )
#         try:
#             user = method(*args, **kwargs)

#             if user:
#                 user.is_active = True
#                 user.is_verified = True
#                 user.is_email_verified = True
#                 user.save()
#                 refresh: RefreshToken = RefreshToken.for_user(user)
#                 return Response(
#                     {
#                         "access": str(refresh.access_token),
#                         "refresh": str(refresh),
#                         "is_staff": user.is_staff,
#                         "user_id": user.id,
#                         "email": user.email,
#                     },
#                     200,
#                 )

#             return Response(
#                 {
#                     "status": status.HTTP_400_BAD_REQUEST,
#                     "message": "Invalid Token or User not found.",
#                 }
#             )
#         except ValidationError as e:
#             return Response(
#                 {
#                     "status": status.HTTP_400_BAD_REQUEST,
#                     "message": str(e),
#                 },
#                 status=400,
#             )
#         except Exception as e:
#             print(f"Unexpected error in social login: {str(e)}")
#             return Response(
#                 {
#                     "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     "message": "An unexpected error occurred.",
#                 },
#                 status=500,
#             )

#     def social_google_oauth2(self, *args, **kwargs):
#         """
#         Handles direct Google OAuth2 tokens (from Google Sign-In)
#         """
#         credential = self.request.data.get("credential")
#         if not credential:
#             raise ValidationError("No credential provided.")

#         try:
#             # For Google ID tokens, decode the payload
#             data = json.loads(urlsafe_base64_decode(credential.split(".")[1]).decode())

#             # Verify the token with Google
#             idinfo = id_token.verify_oauth2_token(
#                 credential,
#                 google_requests.Request(),
#                 settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
#             )
#             print("Google token verified:", idinfo)
#         except ValueError as e:
#             print(f"Google token verification failed: {str(e)}")
#             raise ValidationError("Invalid Google token.")

#         email = data["email"]
#         fcm_token = self.request.data.get("fcm_token")

#         if self.request.user.is_authenticated:
#             user = self.request.user
#         else:
#             user, created = User.objects.get_or_create(
#                 email=email,
#                 defaults={
#                     "first_name": data.get("given_name", ""),
#                     "last_name": data.get("family_name", ""),
#                     "password": data.get("jti") or generate_random_password(),
#                     "is_verified": True,
#                     "is_email_verified": True,
#                     "username": re.sub(r"[\s@.]", "_", email),
#                     "social_only": True,
#                 },
#             )
#             if created:
#                 user.set_password(data.get("jti") or generate_random_password())
#                 user.save()
#                 try:
#                     student_group = Group.objects.get(name="Student")
#                     user.groups.add(student_group)
#                 except Group.DoesNotExist:
#                     pass

#         if fcm_token:
#             register_fcm_device(user, self.request)

#         # Handle UserSocialAuth
#         try:
#             UserSocialAuth.objects.get(uid=email, provider="google-oauth2", user=user)
#         except UserSocialAuth.DoesNotExist:
#             if UserSocialAuth.objects.filter(
#                 uid=email, provider="google-oauth2"
#             ).exists():
#                 raise ValidationError(
#                     {
#                         "non_field_errors": [
#                             "Email has already been linked to other account."
#                         ]
#                     }
#                 )
#             elif user.email and email != user.email:
#                 raise ValidationError(
#                     {
#                         "non_field_errors": [
#                             "The account email address is different from social account email address. "
#                             "Please try with the email address used in the LMS account."
#                         ]
#                     }
#                 )
#             UserSocialAuth.objects.create(
#                 uid=email, provider="google-oauth2", user=user, extra_data=data
#             )

#         update_last_login(user, user)
#         return user

#     def social_clerk(self, *args, **kwargs):
#         token = self.request.data.get("credential")
#         # print(f"Received Clerk token: ")
#         if not token:
#             raise ValidationError("No token provided.")

#         try:
#             # Step 1: Fetch Clerk's public keys
#             jwks_response = requests.get(settings.CLERK_JWKS_URL, timeout=10)
#             jwks_response.raise_for_status()
#             jwks = jwks_response.json()

#             unverified_header = jwt.get_unverified_header(token)
#             key_id = unverified_header.get("kid")
#             if not key_id:
#                 raise ValidationError("No key ID found in token header.")

#             key = next((k for k in jwks["keys"] if k["kid"] == key_id), None)
#             if not key:
#                 raise ValidationError("Matching public key not found.")

#             public_key = algorithms.RSAAlgorithm.from_jwk(key)

#             # Step 2: Decode and verify token
#             decode_options = {"verify_exp": True}
#             payload = jwt.decode(
#                 token,
#                 public_key,
#                 algorithms=["RS256"],
#                 audience=getattr(settings, "CLERK_AUDIENCE", None),
#                 options=decode_options,
#             )

#         except requests.RequestException as e:
#             raise ValidationError("Failed to fetch verification keys.")
#         except jwt.ExpiredSignatureError:
#             raise ValidationError("Token has expired.")
#         except jwt.InvalidTokenError as e:
#             raise ValidationError("Invalid token format or signature.")
#         except Exception as e:
#             raise ValidationError(f"Token verification failed: {str(e)}")

#         user_id = payload.get("sub")
#         if not user_id:
#             raise ValidationError("User ID (sub) not found in token.")

#         headers = {
#             "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }

#         user_api_url = f"{settings.CLERK_API_BASE}/{user_id}"
#         try:
#             user_resp = requests.get(user_api_url, headers=headers)
#             user_resp.raise_for_status()
#             user_info = user_resp.json()
#         except requests.RequestException as e:
#             print(f"Error fetching user info from Clerk API: {str(e)}")
#             raise ValidationError("Failed to fetch user info from Clerk.")

#         email = None
#         if "email_addresses" in user_info and user_info["email_addresses"]:
#             email = user_info["email_addresses"][0].get("email_address")

#         first_name = user_info.get("first_name") or ""
#         last_name = user_info.get("last_name") or ""
#         full_name = user_info.get("full_name") or f"{first_name} {last_name}".strip()

#         if not email:
#             raise ValidationError("Email not found in Clerk user data.")

#         user, created = User.objects.get_or_create(
#             email=email,
#             defaults={
#                 "first_name": first_name,
#                 "last_name": last_name,
#                 "username": re.sub(r"[\s@.]", "_", email),
#                 "is_verified": True,
#                 "is_email_verified": True,
#                 "social_only": True,
#                 "password": generate_random_password(),
#             },
#         )

#         if created:
#             user.set_password(generate_random_password())
#             user.save()
#             try:
#                 student_group = Group.objects.get(name="Student")
#                 user.groups.add(student_group)
#             except Group.DoesNotExist:
#                 pass

#         fcm_token = self.request.data.get("fcm_token")
#         refresh: RefreshToken = RefreshToken.for_user(user)

#         if fcm_token:
#             register_fcm_device(user, self.request)

#         try:
#             UserSocialAuth.objects.get(uid=email, provider="clerk", user=user)
#         except UserSocialAuth.DoesNotExist:
#             if UserSocialAuth.objects.filter(uid=email, provider="clerk").exists():
#                 raise ValidationError(
#                     {"non_field_errors": ["Email already linked to another account."]}
#                 )
#             elif user.email and email != user.email:
#                 raise ValidationError(
#                     {
#                         "non_field_errors": [
#                             "Account email address differs from social account email. Please use the LMS account email."
#                         ]
#                     }
#                 )
#             UserSocialAuth.objects.create(
#                 uid=email, provider="clerk", user=user, extra_data=user_info
#             )

#         update_last_login(user, user)
#         return user
