from rest_framework.routers import DefaultRouter
from cms.viewsets.blogcategory_views import BlogCategoryViewSet
from cms.viewsets.blog_views import BlogViewSet
from cms.viewsets.contactus_views import ContactUsViewSet
router = DefaultRouter()
router.register(r'blog-categories', BlogCategoryViewSet, basename='category')
router.register(r'blogs', BlogViewSet, basename='blog')
router.register(r'contact-us', ContactUsViewSet, basename='contact-us')

urlpatterns = router.urls
