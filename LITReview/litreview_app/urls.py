from django.urls import path
from . import views


urlpatterns = [
    # ... autres URLs ...
    path('', views.HomeView.as_view(), name='home'),

    path('flux/', views.FluxView.as_view(), name='flux'),
    path('posts/', views.PostsView.as_view(), name='posts'),

    path('create_ticket/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('create_ticket/<int:ticket_id>/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('ticket/<int:ticket_id>/edit/', views.EditTicketView.as_view(), name='edit_ticket'),
    path("ticket/<int:ticket_id>/delete/", views.DeleteTicketView.as_view(), name="delete_ticket"),

    path('create_review/', views.CreateReviewView.as_view(), name='create_review'),
    path('review/<int:review_id>/review/', views.EditReviewView.as_view(), name='edit_review'),
    path('review/<int:review_id>/delete/', views.DeleteReviewView.as_view(), name='delete_review'),

    path('review/ticket_id_<int:ticket_id>/create/',
         views.CreateTicketAndReviewView.as_view(), name='create_review_and_ticket'),

    path('followers/', views.FollowersView.as_view(), name='followers'),
    path('delete_user_follow/<int:followed_user_id>/delete/', views.DeleteUserFollowView.as_view(),
         name='delete_user_follow'),


]
