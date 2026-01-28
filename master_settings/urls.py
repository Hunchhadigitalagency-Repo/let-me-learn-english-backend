from rest_framework.routers import DefaultRouter
from master_settings.viewsets.instruction_template_viewsets import InstructionTemplateViewSet

router = DefaultRouter()
router.register(
    r'instruction-template',
    InstructionTemplateViewSet,
    basename='admin-instruction-template'
)

urlpatterns = router.urls
