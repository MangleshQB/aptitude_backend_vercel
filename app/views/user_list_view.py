from django.contrib.auth.models import Group
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.models import CustomUser
from app.serializers import CustomUserSerializer


class UserListView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer

    def list(self, request, *args, **kwargs):
        group_name = request.GET.get('group', None)
        if group_name:
            print(f"Requested group: {group_name}")
            try:
                group = Group.objects.get(name=group_name)
                print(f"Group found: {group}")
                user_data = CustomUser.objects.filter(groups=group)
            except:
                print(f"Group '{group_name}' does not exist.")
        else:
            print("No group specified")
            user_data = CustomUser.objects.all()
        serializer = self.get_serializer(user_data, many=True)
        return Response(serializer.data)