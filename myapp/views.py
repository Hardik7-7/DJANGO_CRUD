from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import EmployeeSerializer,LogoutSerializer,LoginSerializer,TokenSerializer,ProjectDetailsSerializer
from rest_framework.response import Response
from rest_framework import status 
from .models import Employee,ProjectDetails
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken,OutstandingToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.permissions import IsAuthenticated,AllowAny
from .permissions import IsAdminUser,IsValidAccessToken
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from drf_yasg.utils import swagger_auto_schema
from datetime import date
from .models import AccessToken

class CustomTokenRefreshView(TokenViewBase):
    authentication_classes = []
    permission_classes=[AllowAny]
    @swagger_auto_schema(
        operation_description="Renew Your Access Token",
        request_body=LogoutSerializer,
        responses={200: TokenSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)  
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            return Response({'access': access_token}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid token or expired'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    authentication_classes = []
    permission_classes=[AllowAny]
    @swagger_auto_schema(
        operation_description="Register Yourself",
        request_body=EmployeeSerializer,
        responses={200: EmployeeSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            password = validated_data.pop('password')
            projects = validated_data.pop('projects', None)

            employee = Employee(**validated_data)
            employee.set_password(password)
            employee.save()
            if projects:
                employee.projects.set(projects)
            response_data = EmployeeSerializer(employee).data
            response_data.pop('password', None)
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    authentication_classes = []
    permission_classes= [AllowAny]
    @swagger_auto_schema(
        operation_description="Login using email and password",
        request_body=LoginSerializer,
        responses={200: TokenSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                try:
                    BlacklistedToken.objects.create(token=token)
                except:
                    pass 

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            AccessToken.objects.create(token=access_token, user=user)
            refresh_token = str(refresh)
            
            return Response({
                'access': access_token,
                'refresh': refresh_token
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Renew Your Access Token",
        request_body=LogoutSerializer,
        responses={205: "Logout Successfull", 400: 'Bad Request'}
    )
    def post(self, request):
        token = request.auth

        try:
            access_token = AccessToken.objects.get(token=token)
            access_token.is_valid = False
            access_token.save()
        except AccessToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"detail":"You have succssfully Logout"},status=status.HTTP_205_RESET_CONTENT)
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#ADMIN SPECEFIC

class EmployeeListAll(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Getting all Employees (For Admin)",
        responses={200: EmployeeSerializer, 400: 'Bad Request'}
    )
    def get(self,request):
        employee = Employee.objects.all()
        serializer = EmployeeSerializer(employee,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class EmployeeSearch(APIView):
    permission_classes =[IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Get Specefic Employee (For Admin)",
        responses={200: EmployeeSerializer, 404: 'Employee Not Found'}
    )
    def get(self, request, pk):
            employee = get_object_or_404(Employee, pk=pk)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data,status=status.HTTP_200_OK)
    
class EmployeeUpdate(APIView):
    permission_classes =[IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Editing Data Of Any User",
        request_body=EmployeeSerializer,
        responses={200: EmployeeSerializer, 400: 'Bad Request'}
    )
    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            password = validated_data.pop('password', None)
            projects = validated_data.pop('projects', None)
            
            employee = serializer.update(employee, validated_data)
            
            if password:
                employee.set_password(password)
                employee.save()
            
            if projects is not None:
                employee.projects.set(projects)
            
            response_data = EmployeeSerializer(employee).data
            response_data.pop('password', None)
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Deleting an Employee (For Admin)",
        responses={205: "Deleted Employee Successfully", 404: 'Employee Not Found'}
    )
    def delete(self, request,pk):
         employee = get_object_or_404(Employee, pk=pk)
         employee.delete()
         return Response({"detail":"DELETED"})

#USER SPECEFIC

class EmployeeSelf(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken]

    @swagger_auto_schema(
        operation_description="Get Your Own Details (For Admin/User)",
        responses={200: EmployeeSerializer, 404: 'Employee Not Found'}
    )
    def get(self, request):
            employee = get_object_or_404(Employee, pk=request.user.id)
            serializer = EmployeeSerializer(employee)
            return Response(serializer.data,status=status.HTTP_200_OK)      

class EmployeeSelfUpdate(APIView):
    permission_classes =[IsAuthenticated,IsValidAccessToken]
    @swagger_auto_schema(
        operation_description="Editing Data",
        request_body=EmployeeSerializer,
        responses={200: EmployeeSerializer, 400: 'Bad Request'}
    )
    def put(self, request):
        employee = get_object_or_404(Employee, pk=request.user.id)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            password = validated_data.pop('password', None)
            projects = validated_data.pop('projects', None)
            
            employee = serializer.update(employee, validated_data)
            
            if projects is not None:
                return Response({"detail":"You Cannot Update Your Own Projects"},status=status.HTTP_403_FORBIDDEN)  

            if password:
                employee.set_password(password)
                employee.save()
            
            
            response_data = EmployeeSerializer(employee).data
            response_data.pop('password', None)
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#PROJECT API'S

class ProjectPost(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Post New Projects",
        request_body=ProjectDetailsSerializer,
        responses={200: TokenSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = ProjectDetailsSerializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data.get('start_date')
            end_date = serializer.validated_data.get('end_date')

            if start_date and end_date and start_date >= end_date:
                return Response({'error': 'Invalid start date. End Date must be after start date'}, status=status.HTTP_400_BAD_REQUEST)

            if start_date and end_date:
                duration = (end_date - start_date).days 
                serializer.validated_data['estimated_span_in_days'] = duration
            elif end_date:
                today = date.today()
                duration = (end_date - today).days
                serializer.validated_data['estimated_span_in_days'] = duration
            else:
                serializer.validated_data['estimated_span_in_days'] = 90

            project = serializer.save()
            return Response(ProjectDetailsSerializer(project).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProjectAll(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken,IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get All Projects (For Admin)",
        responses={200: ProjectDetailsSerializer, 404: 'Admin/Project Not Found'}
    )
    def get(self, request):
        projects = ProjectDetails.objects.all()
        serializer = ProjectDetailsSerializer(projects,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ProjectSpecefic(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Get Specefic Project (For Admin)",
        responses={200: ProjectDetailsSerializer, 404: 'Project Not Found'}
    )
    def get(self, request,pk):
        project = get_object_or_404(ProjectDetails, pk=pk)
        serializer = ProjectDetailsSerializer(project)
        return Response(serializer.data,status=status.HTTP_200_OK)

class ProjectUpdate(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Edit Projects",
        request_body=ProjectDetailsSerializer,
        responses={200: ProjectDetailsSerializer, 400: 'Bad Request'}
    )
    def put(self, request, pk):
        project = get_object_or_404(ProjectDetails, pk=pk)
        serializer = ProjectDetailsSerializer(project, data=request.data, partial=True)
        
        if serializer.is_valid():
            start_date = serializer.validated_data.get('start_date', project.start_date)
            end_date = serializer.validated_data.get('end_date', project.end_date)
            
            if start_date and end_date and start_date >= end_date:
                return Response({'error': 'Invalid Date Request'}, status=status.HTTP_400_BAD_REQUEST)
            
            if start_date and end_date:
                duration = (end_date - start_date).days
                serializer.validated_data['estimated_span_in_days'] = duration
            elif end_date:
                duration = (end_date - date.today()).days
                serializer.validated_data['estimated_span_in_days'] = duration
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDelete(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken,IsAdminUser]
    @swagger_auto_schema(
        operation_description="Delete Project",
        responses={200:'Project Deleted', 404: 'Project Not Found'}
    )
    def delete(self, request, pk):
        project = get_object_or_404(ProjectDetails, pk=pk)
        project.delete()
        return Response({"detail:Project Deleted"},status=status.HTTP_200_OK)

class ProjectSelf(APIView):
    permission_classes = [IsAuthenticated,IsValidAccessToken]
    @swagger_auto_schema(
        operation_description="Get Details of Project Assigned (For Admin/User)",
        responses={200: ProjectDetailsSerializer, 404: 'Employee/Project Not Found'}
    )
    def get(self, request):
        employee = get_object_or_404(Employee, pk=request.user.id)
        projects = employee.projects.all()
        serializer = ProjectDetailsSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
