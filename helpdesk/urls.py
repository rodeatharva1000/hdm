from django.urls import path
from . import views

urlpatterns = [
    path('help/', views.help_view, name='help'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('show-feedback/', views.show_user_feedback, name='show_feedback'),
    path('show-help/', views.show_user_help, name='show_help'),
    path('help-details/<int:helpid>', views.show_help_details, name='show_help_details'),
    path('feedback-details/<int:feedbackid>', views.show_feedback_details, name='show_feedback_details'),
    path('delete-help/<int:id>', views.delete_help, name='delete_help'),
    path('delete-feedback/<int:id>', views.delete_feedback, name='delete_feedback'),
    path('edit-feedback/<int:id>', views.edit_feedback, name='edit_feedback'),
    path('edit-help/<int:id>', views.edit_help, name='edit_help'),
    path('to_reply', views.reply_view, name='to_reply'),
    path('reply/<int:id>', views.reply, name='reply')
]
