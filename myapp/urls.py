from django.contrib import admin
from django.urls import path,include
from .views import RegisterView,ProjectAll,ProjectFilter,EmployeeFilter,ProjectSelf,EmployeeSearch,EmployeeSelfUpdate,EmployeeUpdate,ProjectDelete,ProjectUpdate,ProjectSpecefic,LoginView,EmployeeListAll,EmployeeSelf,ProjectPost,LogoutView,CustomTokenRefreshView

urlpatterns = [
    path('Register/',RegisterView.as_view()),
    path('Login/',LoginView.as_view()),
    path('Logout/',LogoutView.as_view()),
    path('Refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    #EMPLOYEE API
    path('employee/self/', EmployeeSelf.as_view(), name='employee-detail'),
    path('employee/self/update/', EmployeeSelfUpdate.as_view(), name='employee-detail'),
    path('employee/search/all/', EmployeeListAll.as_view(), name='employee-detail'),
    path('employee/search/<int:pk>/', EmployeeSearch.as_view(), name='employee-detail'),
    path('employee/update/<int:pk>/', EmployeeUpdate.as_view(), name='employee-detail'),
    #PROJECT API
    path('project/self',ProjectSelf.as_view()),
    path('project/post/',ProjectPost.as_view()),
    path('project/all/',ProjectAll.as_view()),
    path('project/search/<int:pk>/',ProjectSpecefic.as_view()),
    path('project/update/<int:pk>/',ProjectUpdate.as_view()),
    path('project/delete/<int:pk>/',ProjectDelete.as_view()),

    #
    path('employee/filter',EmployeeFilter.as_view()),
    path('project/filter',ProjectFilter.as_view())
]
