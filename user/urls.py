
from django.urls import path, include




from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,   # to get access + refresh token
    TokenRefreshView,       # to refresh access token
    TokenVerifyView,
)


from user.viewsets.auth_views import LoginView,  VerifyResetView, ResetPasswordView,UserProfileUpdateView,LogoutView,ChangePasswordView,RegisterView ,VerifyEmailView,DisableAccountAPIView,DeleteAccountAPIView,ForgotPasswordView
from django.urls import path, include

from user.viewsets.student_views import StudentRegisterView,StudentLoginView
from user.viewsets.school_views import SchoolGoogleLoginView,SchoolViewSet
# user_profile_list = UserWithProfileViewSet.as_view({'get': 'list'})

from user.viewsets.address_views import CountryViewSet,ProvinceViewSet,DistrictViewSet

router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'provinces', ProvinceViewSet, basename='provinces')
router.register(r'districts', DistrictViewSet, basename='districts')

router.register(r'schools', SchoolViewSet, basename='school')


urlpatterns = [
    # google login
    
    path('email-verify/<str:token>/',VerifyEmailView.as_view(),name="email-verify"),
    path('', include(router.urls)),

    #app googlelogin
    # path("auth/google/login/", GoogleLoginView.as_view(), name="google-login"),
    
    path('auth/school-google/login/',SchoolGoogleLoginView.as_view(),name="school-google-login"),
   
    path("auth/register/",RegisterView.as_view(),name='register'),

    # admin 
    path("auth/login/", LoginView.as_view(), name="admin-login"),
    path("auth/logout/",LogoutView.as_view(),name="logout"),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # <-- verify token

    
   

    path("auth/change-password/",ChangePasswordView.as_view(), name="change-password"),
    # forgot password
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/verify-reset/",  VerifyResetView.as_view(), name="verify-reset"),
    path("auth/reset-password/",  ResetPasswordView.as_view(), name="reset-password"),
    path("auth/profile/",UserProfileUpdateView.as_view(),name="profile-update"),
    # path("auth/user-profiles/",RegularUserProfileViewSet.as_view({'get': 'list'}), name="user-profiles"),
    
   
    # path("admin/",AdminUserAPIView.as_view(), name="admin-user"),
    # path("admin/<int:user_id>/",AdminUserAPIView.as_view(), name="admin-user-detail"),

    #user_reg_sms

   

  
    #roles and permissions
   
    # path('admin-dropdown/',AdminUserProfileViewSet.as_view({'get': 'list'}), name='admin-user-dropdown'),
  
  
    path('disable-account/', DisableAccountAPIView.as_view(), name='disable-account'),
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),
    # path('check-password/', check_password, name='check-password'),
    # path('delete-user/', DeleteUserAPIView.as_view(), name='delete-user'),
    path('auth/student-register/',StudentRegisterView.as_view(),name='student-register'),
    path('auth/student-login/',StudentLoginView.as_view(),name='student-login'),
    
   
    # path('auth/school-register/',SchoolRegistrationView.as_view(),name='school-register'),
   
   

    path("accounts/", include("allauth.urls")),


   

]

