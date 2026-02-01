from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# =========================
# ViewSets
# =========================
from user.viewsets.user_management_views import UserDropdownAPIView, UserViewSet
from user.viewsets.address_views import (
    CountryViewSet,
    ProvinceViewSet,
    DistrictViewSet,
)
from user.viewsets.school_views import (
    SchoolGoogleLoginView,
    SchoolViewSet,
)

# =========================
# Auth / User Views
# =========================
from user.viewsets.auth_views import (
    LoginView,
    LogoutView,
    RegisterView,
    VerifyEmailView,
    ChangePasswordView,
    ForgotPasswordView,
    VerifyResetView,
    ResetPasswordView,
    UserProfileUpdateView,
    DisableAccountAPIView,
    DeleteAccountAPIView,
)

from user.viewsets.student_views import (
    StudentRegisterView,
    StudentLoginView,
    StudentEditView,
)
from user.viewsets.school_views import SchoolDropdownViewSet
from user.viewsets.role_permissions_view import RolePermissionViewSet
# =========================
# Routers
# =========================
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'provinces', ProvinceViewSet, basename='provinces')
router.register(r'districts', DistrictViewSet, basename='districts')
router.register(r'schools', SchoolViewSet, basename='schools')
router.register(r'user-management', UserViewSet, basename='user-management')

router.register(
    r"schools-dropdown",
    SchoolDropdownViewSet,
    basename="schooldropdown"
)

# =========================
# URL Patterns
# =========================
urlpatterns = [

    # -------- Email Verification --------
    path('email-verify/<str:token>/', VerifyEmailView.as_view(), name="email-verify"),

    # -------- Router URLs --------
    path('', include(router.urls)),

    # -------- Google Login --------
    path('auth/school-google/login/', SchoolGoogleLoginView.as_view(), name="school-google-login"),

    # -------- Authentication --------
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name="admin-login"),
    path('auth/logout/', LogoutView.as_view(), name="logout"),

    # -------- JWT --------
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # -------- Password --------
    path('auth/change-password/', ChangePasswordView.as_view(), name="change-password"),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name="forgot-password"),
    path('auth/verify-reset/', VerifyResetView.as_view(), name="verify-reset"),
    path('auth/reset-password/', ResetPasswordView.as_view(), name="reset-password"),

    # -------- Profile --------
    path('auth/profile/', UserProfileUpdateView.as_view(), name="profile-update"),

    # -------- Account --------
    path('disable-account/', DisableAccountAPIView.as_view(), name='disable-account'),
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),

    # -------- Student Auth --------
    path('auth/student-register/', StudentRegisterView.as_view(), name='student-register'),
    path('auth/student-login/', StudentLoginView.as_view(), name='student-login'),

    # -------- Student Edit --------
    path('school-student-edit/', StudentEditView.as_view(), name='student-edit'),
    path('school-student-edit/<int:student_id>/', StudentEditView.as_view(), name='student-edit'),

    #----------- User Management ----------
    path('user-management/dropdown/', UserDropdownAPIView.as_view(), name='user-dropdown'),
    
    
    path('roles/', RolePermissionViewSet.as_view({'get': 'list_roles'}), name='list-roles'),
    path('roles/<int:pk>/', RolePermissionViewSet.as_view({'get': 'list_roles'}), name='list-roles'),
    path('roles/create/', RolePermissionViewSet.as_view({'post': 'create_role_and_permission'}), name='create-role'),
    path('roles/<int:pk>/update/', RolePermissionViewSet.as_view({'patch': 'update_role_and_permission'}), name='update-role'),
    path('roles/<int:pk>/delete/', RolePermissionViewSet.as_view({'delete': 'delete_role'}), name='delete-role'),


    # -------- AllAuth --------
    path('accounts/', include('allauth.urls')),
]
