from rest_framework import serializers
from .models import Employee,ProjectDetails

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="Access token")
    refresh = serializers.CharField(help_text="Refresh token")

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(help_text="Refresh token")

class EmployeeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=ProjectDetails.objects.all(), many=True, required=False)
    
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'password', 'date_joined', 'projects']
        extra_kwargs = {
            'date_joined': {'read_only': True}
        }
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['date_joined'] = instance.date_joined.strftime('%Y-%m-%d') if instance.date_joined else None
        return representation
    
    def validate_email(self, value):
        user = self.instance
        if user and Employee.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        elif not user and Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
   
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'password', 'date_joined']
        extra_kwargs = {
            'date_joined': {'read_only': True}
        }
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['date_joined'] = instance.date_joined.strftime('%Y-%m-%d') if instance.date_joined else None
        return representation
    
    def validate_email(self, value):
        user = self.instance
        if user and Employee.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        elif not user and Employee.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

class ProjectDetailsSerializer(serializers.ModelSerializer):
    employees = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), many=True)

    class Meta:
        model = ProjectDetails
        fields = ['name', 'description', 'start_date', 'end_date', 'estimated_span_in_days', 'status', 'employees']
        extra_kwargs = {
            'estimated_span_in_days': {'read_only': True},
            'start_date': {'required': False},
            'end_date': {'required': False},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['estimated_span_in_days'] = instance.estimated_span_in_days
        return representation