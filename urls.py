"""
Norm the compass URL config
"""

from django.urls import path

from ntc import views

urlpatterns = [

    # HTML views
    path('', views.home),
    path('vote/', views.vote),
    path('vote/<int:topic_id>/', views.topic),

    # User views
    path('login_user/', views.login_user),
    path('signup/', views.signup),
    path('logout/', views.logout_user),

    # API views
    path('create_topic/', views.create_topic),
    path('check_topic_duplicates/', views.check_topic_duplicates),
    path('search_topic', views.search_topic),
    path('get_topic/<int:topic_id>/', views.get_topic),
    path('next_topic/', views.next_topic),
    path('random_topic/', views.random_topic),
    path('submit_vote/', views.submit_vote),
    path('skip_topic/', views.skip_topic),
    path('submit_comment/', views.submit_comment),
    path('submit_comment_vote/', views.submit_comment_vote),
    ]
