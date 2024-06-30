from django.urls import path
from .views import AllBlogPostsView, BlogPostDetailView

app_name = "blog"
urlpatterns = [
	path("post/<slug:slug>/", BlogPostDetailView.as_view(), name="detail"),
	path("", AllBlogPostsView.as_view(), name="all_posts")
]