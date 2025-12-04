from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('Forgot_Password/', views.Forgot_Password, name='Forgot_Password'),


    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('project/<int:project_id>/', views.project_details, name='project_details'),
    path('personal_project/<int:project_id>/', views.personal_project_details, name='personal_project_details'),
    path('personal_project/<int:project_id>/upload_certificate/', views.upload_utilization_certificate, name='upload_utilization_certificate'),
    path('project/<int:project_id>/view_certificates/', views.view_utilization_certificates, name='view_utilization_certificates'),
    path('project/<int:project_id>/apply/', views.apply_for_project, name='apply_for_project'),
    path('apply_for_ipr/', views.apply_for_ipr, name='apply_for_ipr'),
    path('download_ppt/', views.download_ppt, name='download_ppt'),
    path('project/<int:project_id>/save-utilization/', views.save_utilization, name='your_new_utilization_view_url'),
    path("project/<int:project_id>/update-group-photo/", views.update_group_photo, name="update_group_photo"),
    path("project/<int:project_id>/update-product-photo/", views.update_product_photo, name="update_product_photo"),

    path('college_dashboard/', views.college_dashboard, name='college_dashboard'),
    path('student_requests/', views.student_requests, name='student_requests'),
    path('approve_request/<str:app_type>/<int:app_id>/', views.approve_request, name='approve_request'),
    path('approve_ipr_request/<str:app_type>/<int:app_id>/', views.approve_ipr_request, name='approve_ipr_request'),
    path('add_project/', views.add_project, name='add_project'),
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('unauthorized/', views.unauthorized_view, name='unauthorized'),


]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

 