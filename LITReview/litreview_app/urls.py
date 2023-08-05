from django.urls import path
from . import views


urlpatterns = [
    # ... autres URLs ...
    path('', views.HomeView.as_view(), name='home'),

    path('flux/', views.FluxView.as_view(), name='flux'),
    path('posts/', views.PostsView.as_view(), name='posts'),

    path('create_ticket/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('edit_ticket/<int:ticket_id>/', views.EditTicketView.as_view(), name='edit_ticket'),
    path('delete_ticket/<int:ticket_id>/', views.DeleteTicketView.as_view(), name='delete_ticket'),

    path('create_review/', views.CreateReviewView.as_view(), name='create_review'),
    path('create_review/<int:ticket_id>/', views.CreateReviewView.as_view(), name='create_review'),
    path('edit_review/<int:review_id>/', views.EditReviewView.as_view(), name='edit_review'),
    path('delete_review/<int:review_id>/', views.EditReviewView.as_view(), name='delete_review'),

    path('followers/', views.FollowersView.as_view(), name='followers'),
    path("delete/<int:id_delete>/", views.DeleteUserFollowView.as_view(), name="delete"),

    #path("modify/<str:content>/<int:id_modify>/", views.ModifyContentView.as_view(), name='modify_content'),
    #path("delete/<str:content>/<int:id_delete>/", views.DeleteContentView.as_view(), name='delete_content'),


]