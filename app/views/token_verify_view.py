from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
from app.management.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ParseError, ValidationError


class TokenVerifyView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        jwt_token = request.META.get('HTTP_AUTHORIZATION')
        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)

        if not jwt_token:
            return Response({'error': 'Token is required!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, payload = JWTAuthentication.decode_jwt_token(jwt_token)
            return Response({'status': 'Token is valid'}, status=status.HTTP_200_OK)

        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error': 'Token verification failed'}, status=status.HTTP_400_BAD_REQUEST)
