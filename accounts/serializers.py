from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    is_premium = serializers.BooleanField(read_only=True)


    class Meta:
        model = CustomUser
        fields = ["username", "email", "age", "bio", "image", "is_premium", "is_staff"]
