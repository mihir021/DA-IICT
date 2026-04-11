from rest_framework import serializers

class SignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    location = serializers.CharField(max_length=100, required=False, default="")

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ExpenseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = serializers.CharField(max_length=50)

class ProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    location = serializers.CharField(max_length=100, required=False)
