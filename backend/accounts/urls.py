from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('signup/', views.signup_page_view, name='signup-page'),
    path('signup-verify/', views.signup_verify_view, name='signup-verify'),
    path('login-verify/', views.login_verify, name='login-verify'),
    path('home/', views.home, name='home'),
    path('notification/', views.notification, name='notification'),
    path('search/', views.search, name='search'),
    path('profile-setup/', views.profile_setup, name='profile-setup'),
    path('profile/<int:user_id>/tree/', views.profile_tree_view, name='profile-tree'),
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints
    path('api/signup/', views.signup, name='signup'),
    path('api/login/', views.login_view, name='login'),
    path('api/profile-setup/', views.profile_setup_api, name='profile-setup-api'),
    path('api/users/', views.get_users_api, name='get-users'),
    path('api/relate/', views.relate_user_api, name='relate-user'),
    path('api/notifications/', views.get_notifications_api, name='get-notifications'),
    path('api/respond-relationship/', views.respond_to_relationship_api, name='respond-relationship'),
    path('api/activity/', views.get_activity_api, name='get-activity'),
    path('api/family-graph/', views.get_family_graph_api, name='get-family-graph'),
    path('api/relation-status/', views.relation_status_api, name='relation-status'),
    path('api/relation-withdraw/', views.relation_withdraw_api, name='relation-withdraw'),
    path('profile-page/', views.profile_page, name='profile-page'),
    path('api/update-profile/', views.update_profile_api, name='update-profile'),
    path('api/update-profile-pic/', views.update_profile_pic_api, name='update-profile-pic'),
    path('api/family-members/', views.get_family_members_api, name='family-members'),
]
