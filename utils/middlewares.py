from rest_framework.permissions import BasePermission
import requests

# Aptitude --> CheckCRMUser, Get_Surveillance_token
# Surveillance --> CheckUser, Get_JWT_token
class CheckCRMUser(BasePermission):
    """
        Check if provided JWT token is valid or not using .Net API
    """

    def has_permission(self, request, view):
        #
        # if request.user and request.user.is_authenticated:
        #     return True

        if 'XSRF-TOKEN' not in request.COOKIES or 'worksuite_session' not in request.COOKIES:
            return False

        token = request.COOKIES['XSRF-TOKEN']
        work_suite_session = request.COOKIES['worksuite_session']

        url = "https://crm.quantumbot.in/account/dashboard/private_calendar?start=2024-09-01T00%3A00%3A00&end=2024-09-08T00%3A00%3A00&timeZone=Asia%2FKolkata"

        headers = {
            'Cookie': f'XSRF-TOKEN={token};worksuite_session={work_suite_session}'
        }

        with requests.get(url, headers=headers) as response:
            if response.status_code != 200:
                return False
            if 'crm.quantumbot.in/login' in response.url:
                return False
        return True


def Get_Surveillance_token(request) -> str:
    return request.META.get('HTTP_AUTHORIZATION')


class CheckSoftwareUser(BasePermission):
    def has_permission(self, request, view):

        auth_token = Get_Surveillance_token(request)
        if auth_token is None:
            return False

        headers = {'Authorization': auth_token}

        with requests.get("http://192.168.1.7:8001/api/verify/", headers=headers) as response:
            if response.status_code != 200:
                return False

        return True

def Get_JWT_token(request) -> str:
    return request.META.get('HTTP_AUTHORIZATION')

class CheckUser(BasePermission):
    """
        Check if provided JWT token is valid or not using .Net API
    """

    def has_permission(self, request, view):

        if request.user and request.user.is_authenticated:
            return True

        auth_token = Get_JWT_token(request)
        if auth_token is None:
            return False

        headers = {'Authorization': auth_token, 'Currentappversion': 'v1'}

        # with requests.get("https://bioslabapi.cnetgroup.in/api/v1/Country", headers=headers) as response:
        with requests.get("http://192.168.1.7:8001/aptitude/configuration/", headers=headers) as response:
            if response.status_code != 200:
                return False

        return True
