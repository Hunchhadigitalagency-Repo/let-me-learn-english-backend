from rest_framework.routers import DefaultRouter
from cms.viewsets.blogcategory_views import BlogCategoryViewSet
from cms.viewsets.blog_views import BlogViewSet
from cms.viewsets.contactus_views import ContactUsViewSet
from cms.viewsets.newsletter_views import NewsletterViewSet
from cms.viewsets.knowit_views import NowKnowItViewSet
from cms.viewsets.video_views import VideoViewSet
router = DefaultRouter()
router.register(r'blog-categories', BlogCategoryViewSet, basename='category')
router.register(r'blogs', BlogViewSet, basename='blog')
router.register(r'contact-us', ContactUsViewSet, basename='contact-us')
router.register(r'newsletters', NewsletterViewSet, basename='newsletter')
router.register(r'nowknowit', NowKnowItViewSet, basename='nowknowit')
router.register(r'videos', VideoViewSet, basename='videos')


urlpatterns = router.urls
