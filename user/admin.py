from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, ResetPassword,FocalPerson,SchoolStudentParent,School

# -------------------------
# Custom User Admin
# -------------------------
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    search_fields = ('email', 'name')
    ordering = ('email',)

    # Fields displayed in user detail page
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('name', 'login_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'password1', 'password2'),
        }),
    )


# -------------------------
# UserProfile Admin
# -------------------------
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'display_name',
        'user_type',
        'is_verified',
        'is_disabled',
        'is_deleted',
        'grade',
        'section',
        'student_parent_name',
        'student_parent_email',
        'student_parent_phone_number'
    )
    list_filter = ('user_type', 'is_verified', 'is_disabled', 'is_deleted')
    search_fields = ('user__email', 'display_name', 'student_parent_name', 'student_parent_email')


# -------------------------
# ResetPassword Admin
# -------------------------
class ResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'reset_token', 'created_at')
    search_fields = ('user__email', 'reset_token')


from django.contrib import admin
from .models import Country, Province, District, School


# =========================
# Country Admin
# =========================
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# =========================
# Province Admin
# =========================
@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    list_filter = ('country',)
    search_fields = ('name',)


# =========================
# District Admin
# =========================
@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'province')
    list_filter = ('province',)
    search_fields = ('name',)


# =========================
# School Admin
# =========================
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'code',
        'user',
        'country',
        'province',
        'district',
        'created_at',
    )

    list_filter = (
        'country',
        'province',
        'district',
    )

    search_fields = (
        'name',
        'code',
        'email',
    )

    readonly_fields = (
        'code',
        'created_at',
        'updated_at',
    )

    autocomplete_fields = (
        'country',
        'province',
        'district',
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'name',
                'logo',
                'establish_date',
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'landline',
            )
        }),
        ('Location Information', {
            'fields': (
                'country',
                'province',
                'district',
                'city',
                'address',
            )
        }),
        ('System Information', {
            'fields': (
                'code',
                'created_at',
                'updated_at',
            )
        }),
    )
@admin.register(FocalPerson)
class FocalPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'designation', 'school')
    search_fields = ('name', 'email', 'phone', 'school__name')
    list_filter = ('school',)

# Admin for SchoolStudentParent (separate)
@admin.register(SchoolStudentParent)
class SchoolStudentParentAdmin(admin.ModelAdmin):
    list_display = ('student', 'parent', 'school')
    search_fields = ('student__email', 'parent__email', 'school__name')
    list_filter = ('school',)

# Register the models
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(ResetPassword, ResetPasswordAdmin)
