from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, Group
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication.JWTAuthentication import authenticate
from django.contrib.auth import authenticate
from app.management.authentication import JWTAuthentication
from app.models import EmployeeDetails, Designation, CustomUser
from app.serializers import LoginSerializer
from utils.common import ResponseFormat
from app.models.crm_users import Users as CRMUsers
from utils.functions import check_bcrypt_password
from rest_framework.authtoken.models import Token
import bcrypt


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseFormat().response
        super().__init__(**kwargs)

    @swagger_auto_schema(request_body=LoginSerializer, operation_description="Login API", )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        is_software = serializer.validated_data.get('is_software')


        user = CustomUser.objects.filter(email=email).first()
        user_auth = authenticate(email=email, password=password)
        crm_user_obj = CRMUsers.objects.filter(email=email).using('crm').first()

        check_pas = False
        if crm_user_obj:
            check_pas = bcrypt.checkpw(password.encode('utf-8'), crm_user_obj.password.encode('utf-8'))

        if not user_auth and not crm_user_obj:

            self.response_format['status'] = False
            self.response_format['message'] = 'Invalid credentials'
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        elif user and crm_user_obj and check_pas:
            if not user_auth:
                user.password = make_password(serializer.validated_data.get('password', 'default_password'))
                user.save()

        elif (user_auth and not crm_user_obj) or (not user and crm_user_obj):
            pass

        else:
            self.response_format['status'] = False
            self.response_format['message'] = 'Invalid credentials'
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


        permissions = Permission.objects.filter(group__user=user).distinct().count()

        if user:
            if permissions == 0 and not is_software:
                self.response_format['status'] = False
                self.response_format['message'] = 'Contact your admin for Login Approval'
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

        if user:
            if is_software == True:
                token, created = Token.objects.get_or_create(user=user)
                self.response_format['data'] = {
                    'token': token.key,
                    'email': user.email if user.email else '',
                    'first_name': user.first_name if user.first_name else '',
                    'last_name': user.last_name if user.last_name else '',
                    'phone_number': user.phone_number if user.phone_number else '',
                    'is_surveillance_active': user.is_surveillance_active
                }
            else:
                access, refresh = JWTAuthentication.create_jwt(user)
                self.response_format['data'] = {
                    'access': access,
                    'refresh': refresh,
                    'email': user.email if user.email else '',
                    'first_name': user.first_name if user.first_name else '',
                    'last_name': user.last_name if user.last_name else '',
                    'phone_number': user.phone_number if user.phone_number else '',
                    'is_surveillance_active': user.is_surveillance_active
                }

            self.response_format['status'] = True
            self.response_format['message'] = 'Login Successful'
            return Response(self.response_format, status=status.HTTP_200_OK)
        elif not user:
            try:
                # Fetch CRM Details
                crm_user = CRMUsers.objects.filter(email=email).using('crm').first()
                if not crm_user:
                    self.response_format['status'] = False
                    self.response_format['message'] = 'Invalid credentials'
                    return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

                # Match CRM Password
                if not bcrypt.checkpw(password.encode('utf-8'), crm_user_obj.password.encode('utf-8')):
                    self.response_format['status'] = False
                    self.response_format['message'] = 'Invalid credentials'
                    return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

                crm_desi = EmployeeDetails.objects.filter(user=crm_user).using('crm').first()

                crm_designation = crm_desi.designation.name if crm_desi and crm_desi.designation else None
                crm_date_of_birth = crm_desi.date_of_birth if crm_desi and crm_desi.date_of_birth else None
                crm_joining_date = crm_desi.joining_date if crm_desi and crm_desi.joining_date else None

                designation_obj, created = Designation.objects.get_or_create(
                    name=crm_designation or 'Default Designation')

                name = crm_user.name if crm_user and crm_user.name else serializer.validated_data.get('email')
                first_name, last_name = (name.split(' ')[0], name.split(' ')[1]) if ' ' in name else (name, "")

                hashed_password = make_password(serializer.validated_data.get('password', 'default_password'))

                create_user = CustomUser.objects.create(
                    designation=designation_obj,
                    email=serializer.validated_data.get('email'),
                    username=serializer.validated_data.get('email'),
                    first_name=first_name if first_name else '',
                    last_name=last_name if last_name else '',
                    password=hashed_password,
                    phone_number=crm_user.mobile if crm_user and crm_user.mobile else None,
                    joining_date=crm_joining_date.date() if crm_joining_date else None,
                    date_of_birth=crm_date_of_birth if crm_date_of_birth else None
                )

                # crm_desi = EmployeeDetails.objects.filter(user=crm_user).using('crm').first()
                # crm_designation = crm_desi.designation.name
                # crm_date_of_birth = crm_desi.date_of_birth
                # crm_joining_date = crm_desi.joining_date
                # designation_obj, created = Designation.objects.get_or_create(name=crm_designation)
                # name = crm_user.name
                # first_name = name.split(' ')[0]
                # last_name = name.split(' ')[1]
                # hashed_password = make_password(serializer.validated_data.get('password'))
                # create_user = CustomUser.objects.create(designation=designation_obj,
                #                                         email=serializer.validated_data.get('email'),
                #                                         username=serializer.validated_data.get('email'),
                #                                         first_name=first_name, last_name=last_name,
                #                                         password=hashed_password, phone_number=crm_user.mobile,
                #                                         joining_date=crm_joining_date.date(),
                #                                         date_of_birth=crm_date_of_birth)
                print(create_user)
                user = authenticate(email=email, password=password)
                if user:
                    groups = Group.objects.filter(name='Employee').first()
                    if groups:
                        create_user.groups.add(groups)
                    # print(groups)
                    permissions = Permission.objects.filter(group__user=user).distinct().count()
                    if permissions == 0 and not is_software:
                        user.save()
                        self.response_format['status'] = False
                        self.response_format['message'] = 'Contact your admin for Login Approval'
                        return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)

                    if is_software == True:
                        token, created = Token.objects.get_or_create(user=user)
                        self.response_format['data'] = {
                            'token': token.key,
                            'email': user.email if user.email else '',
                            'first_name': user.first_name if user.first_name else '',
                            'last_name': user.last_name if user.last_name else '',
                            'phone_number': user.phone_number if user.phone_number else '',
                            'is_surveillance_active': user.is_surveillance_active
                        }
                        # print(self.response_format['data'])
                    else:
                        access, refresh = JWTAuthentication.create_jwt(user)
                        self.response_format['data'] = {
                            'access': access,
                            'refresh': refresh,
                            'email': user.email if user.email else '',
                            'first_name': user.first_name if user.first_name else '',
                            'last_name': user.last_name if user.last_name else '',
                            'phone_number': user.phone_number if user.phone_number else '',
                            'is_surveillance_active': user.is_surveillance_active
                        }
                        print(self.response_format['data'])
                    user.is_surveillance_active = True
                    user.save()
                    self.response_format['status'] = True
                    self.response_format['message'] = 'Login Successful'
                    return Response(self.response_format, status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                self.response_format['status'] = False
                self.response_format['message'] = e
                return Response(self.response_format, status=status.HTTP_200_OK)
