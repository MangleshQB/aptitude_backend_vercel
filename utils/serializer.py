from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model

user = get_user_model()


class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop("serializer", None)
        if self.serializer is not None and not issubclass(
                self.serializer, serializers.Serializer
        ):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)


class RefUserSerializer(ModelSerializer):
    class Meta:
        fields = ('id', 'username', 'email', 'first_name', 'last_name','employee_id')
        model = user


class BaseModelSerializer(ModelSerializer):

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    deleted_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_deleted = serializers.BooleanField(default=False, read_only=True, required=False)

    class Meta:
        abstract = True


class BaseModelSerializerCore(ModelSerializer):
    created_by = RefUserSerializer(read_only=True, allow_null=True)
    updated_by = RefUserSerializer(read_only=True, allow_null=True)
    deleted_by = RefUserSerializer(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True, allow_null=True)
    deleted_at = serializers.DateTimeField(read_only=True, allow_null=True)
    is_deleted = serializers.BooleanField(default=False, read_only=True, required=False)

    def validate(self, attrs):
        if self.context.get("created_by", None):
            attrs['created_by'] = self.context.get("created_by")
        if self.context.get("updated_by", None):
            attrs['updated_by'] = self.context.get("updated_by")
        return attrs

    class Meta:
        abstract = True