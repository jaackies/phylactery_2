from django.urls import path
from .views import AllBlogPostsView

app_name = "blog"
urlpatterns = [
	path("", AllBlogPostsView.as_view(), name="all-posts")
]