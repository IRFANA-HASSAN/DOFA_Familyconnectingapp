from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import UserProfile, FamilyRelationship,PendingSignup

admin.site.register(PendingSignup)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone_number', 'profile_image', 'date_of_birth', 'father_name', 
              'mother_name', 'job', 'country', 'state', 'district', 'location', 
              'is_profile_complete')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('get_profile_picture', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number', 'get_profile_complete')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined', 'profile__is_profile_complete')
    
    def get_profile_picture(self, obj):
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile.profile_image.url
            )
        else:
            return format_html(
                '<img src="/static/assets/np.png" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />'
            )
    get_profile_picture.short_description = 'Profile Picture'
    
    def get_phone_number(self, obj):
        return obj.profile.phone_number if hasattr(obj, 'profile') else 'N/A'
    get_phone_number.short_description = 'Phone Number'
    
    def get_profile_complete(self, obj):
        return obj.profile.is_profile_complete if hasattr(obj, 'profile') else False
    get_profile_complete.short_description = 'Profile Complete'
    get_profile_complete.boolean = True

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('get_profile_picture', 'user', 'phone_number', 'country', 'is_profile_complete', 'created_at')
    list_filter = ('is_profile_complete', 'country', 'state', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'father_name', 'mother_name')
    readonly_fields = ('created_at', 'updated_at', 'get_profile_picture_display')
    
    def get_profile_picture(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_image.url
            )
        else:
            return format_html(
                '<img src="/static/assets/np.png" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />'
            )
    get_profile_picture.short_description = 'Profile Picture'
    
    def get_profile_picture_display(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_image.url
            )
        else:
            return format_html(
                '<img src="/static/assets/np.png" width="100" height="100" style="border-radius: 50%; object-fit: cover;" />'
            )
    get_profile_picture_display.short_description = 'Profile Picture'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'get_profile_picture_display', 'profile_image')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'father_name', 'mother_name', 'job')
        }),
        ('Location', {
            'fields': ('country', 'state', 'district', 'location')
        }),
        ('Status', {
            'fields': ('is_profile_complete', 'created_at', 'updated_at')
        }),
    )

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(FamilyRelationship)
class FamilyRelationshipAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'relationship_type', 'relation_label', 'middle_user', 'status', 'created_at')
    list_filter = ('status', 'relationship_type', 'created_at')
    search_fields = ('from_user__username', 'to_user__username', 'middle_user__username', 'relation_label', 'message')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Relationship Details', {
            'fields': ('from_user', 'to_user', 'relationship_type', 'relation_label', 'middle_user', 'status')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# Customize admin site
admin.site.site_header = "DOFA Admin Panel"
admin.site.site_title = "DOFA Admin"
admin.site.index_title = "Welcome to DOFA Administration"
