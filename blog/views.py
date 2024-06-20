from django.views.generic import ListView
from .models import BlogPost


class AllBlogPostsView(ListView):
	"""
	View that shows a list of all BlogPosts.
	TODO: Let Committee see everything.
	"""
	
	template_name = "blog/blog_list_view.html"
	context_object_name = "blogpost_list"
	model = BlogPost
	paginate_by = 10
	