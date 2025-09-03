import json
from datetime import datetime, timedelta
import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework import HTTP_HEADER_ENCODING, exceptions

User = get_user_model()


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    def get_surveillance_token(self, request) -> str:
        return request.META.get('HTTP_AUTHORIZATION')

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            # raise exceptions.AuthenticationFailed(_('Invalid token.'))
            raise exceptions.AuthenticationFailed(('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def check_surveillance_software_user(self, request, software_token):

        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    # def authenticate(self, request):
    #
    #     token = request.META.get('HTTP_AUTHORIZATION')
    #
    #     jwt_token = token if "Bearer" in token else None
    #     software_token = token if "Token" in token else None
    #
    #     if jwt_token is None and software_token is None:
    #         return None
    #
    #     user, payload = None, None
    #
    #     if software_token:
    #         user, payload = self.check_surveillance_software_user(request, software_token)
    #         return user, payload
    #     else:
    #         jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)  # clean the token
    #
    #         try:
    #             payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
    #         except jwt.exceptions.InvalidSignatureError:
    #             raise AuthenticationFailed('Invalid signature')
    #         except jwt.ExpiredSignatureError:
    #             raise AuthenticationFailed('Token has expired')
    #         except jwt.InvalidTokenError:
    #             raise AuthenticationFailed('Invalid token')
    #         except:
    #             raise ParseError()
    #
    #         # Get the user from the database
    #         username = payload.get('user_identifier')
    #         if username is None:
    #             raise AuthenticationFailed('User identifier not found in JWT')
    #
    #         user = User.objects.filter(username=username).first()
    #         if user is None:
    #             raise AuthenticationFailed('User not found')
    #         return user, payload
    #
    #     return user, payload

    def authenticate(self, request):

        jwt_token = None
        software_token = None

        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            if "Bearer" in token:
                jwt_token = token
            elif "Token" in token:
                software_token = token

        if jwt_token is None and software_token is None:
            return None

        user, payload = None, None

        if software_token:
            user, payload = self.check_surveillance_software_user(request, software_token)
            return user, payload
        else:
            jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)

            try:
                payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            except jwt.exceptions.InvalidSignatureError:
                raise AuthenticationFailed('Invalid signature')
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Token has expired')
            except jwt.InvalidTokenError:
                raise AuthenticationFailed('Invalid token')
            except:
                raise ParseError()

            # Get the user from the database
            username = payload.get('user_identifier')
            if username is None:
                raise AuthenticationFailed('User identifier not found in JWT')

            user = User.objects.filter(username=username).first()
            if user is None:
                raise AuthenticationFailed('User not found')

            return user, payload

    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_jwt(cls, user):
        access_payload = {
            'user_identifier': user.username,
            'exp': int((datetime.now() + settings.JWT_CONF['TOKEN_LIFETIME']).timestamp()),
            'iat': datetime.now().timestamp(),
            'profile_pk': user.id,
            'email': user.email,
            'phone_number': user.phone_number,
            'username': user.username,
        }

        refresh_payload = {
            'user_identifier': user.username,
            'exp': int((datetime.now() + settings.JWT_CONF['REFRESH_TOKEN_LIFETIME']).timestamp()),
            'iat': datetime.now().timestamp(),
            'profile_pk': user.id,
            'email': user.email,
            'phone_number': user.phone_number,
            'username': user.username,
        }

        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        return access_token, refresh_token

    @classmethod
    def get_the_token_from_header(cls, token):
        token = token.replace('Bearer', '').replace(' ', '')
        return token

    @classmethod
    def decode_jwt_token(cls, token, forgot_password: bool = False):
        try:
            if forgot_password:
                payload = jwt.decode(token, settings.FORGOT_PASSWORD_SECRET, algorithms=['HS256'])
            else:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed('Token decoding failed')

        # Get the user from the database
        username = payload.get('user_identifier')
        if username is None:
            raise AuthenticationFailed('User identifier not found in JWT')

        user = User.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found')

        # Return the user and token payload
        return user, payload

    @classmethod
    def generate_new_access_token(cls, refresh_token):
        try:
            # Decode the refresh token to check if it's valid and not expired
            user, refresh_payload = cls.decode_jwt_token(refresh_token)

            access_payload = {
                'user_identifier': user.username,
                'exp': int((datetime.now() + settings.JWT_CONF['TOKEN_LIFETIME']).timestamp()),
                'iat': datetime.now().timestamp(),
                'email': user.email,
                'profile_pk': user.id
            }

            refresh_payload = {
                'user_identifier': user.username,
                'exp': int((datetime.now() + settings.JWT_CONF['REFRESH_TOKEN_LIFETIME']).timestamp()),
                'iat': datetime.now().timestamp(),
                'email': user.email,
                'profile_pk': user.id
            }

            access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
            refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

            return access_token, refresh_token

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid refresh token')

    @classmethod
    def create_forgot_password_token(cls, user):
        token_payload = {
            'user_identifier': user.username,
            'exp': int((datetime.now() + settings.JWT_CONF['FORGOT_PASSWORD_LIFETIME']).timestamp()),
            'iat': datetime.now().timestamp(),
            'email': user.email,
            'profile_pk': user.id
        }

        token = jwt.encode(token_payload, settings.FORGOT_PASSWORD_SECRET, algorithm='HS256')

        return token
