from django.urls import path
from . import views


urlpatterns = [
    # ... autres URLs ...
    path('', views.HomeView.as_view(), name='home'),

    path('flux/', views.FluxView.as_view(), name='flux'),
    path('posts/', views.PostsView.as_view(), name='posts'),

    path('create_ticket/', views.CreateTicketView.as_view(), name='create_ticket'),
    path('create_ticket/<int:ticket_id>/', views.CreateTicketView.as_view(), name='create_ticket'),

    path('create_review/', views.CreateReviewView.as_view(), name='create_review'),
    path('review/ticket_id_<int:ticket_id>/create/',
         views.CreateTicketAndReviewView.as_view(), name='create_review_and_ticket'),

    path('followers/', views.FollowersView.as_view(), name='followers'),
    path("delete/<int:id_delete>/", views.DeleteUserFollowView.as_view(), name="delete"),
    path("modify/<str:content>/<int:id_modify>/", views.ModifyContentView.as_view(), name='modify_content'),
    path("delete/<str:content>/<int:id_delete>/", views.DeleteContentView.as_view(), name='delete_content'),


]
