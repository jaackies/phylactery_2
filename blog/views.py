from django.views.generic import ListView, DetailView
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
	
	def get_queryset(self):
		"""
		Show only published posts by default,
		ordered by most recent.
		"""
		return BlogPost.objects.filter(
			published=True,
		).order_by("-publish_on")
	
class BlogPostDetailView(DetailView):
	"""
	View to show one specific BlogPost.
	Doesn't allow non-Committee members to see non-published posts.
	"""
	model = BlogPost
	template_name = "blog/blog_detail_view.html"
	
	pass
