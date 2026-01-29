from rest_framework.routers import DefaultRouter
from master_settings.viewsets.instruction_template_viewsets import InstructionTemplateViewSet
from master_settings.viewsets.privacy_policy_viewsets import PrivacyPolicyViewSet
from master_settings.viewsets.terms_condition_viewsets import TermsandConditionsViewSet
from master_settings.viewsets.exampause_viewsets import ExamPauseViewSet
router = DefaultRouter()
router.register(
    r'instruction-template',
    InstructionTemplateViewSet,
    basename='admin-instruction-template'
)
router.register(r'privacy-policy', PrivacyPolicyViewSet, basename='privacy-policy')
router.register(r'terms-conditions', TermsandConditionsViewSet, basename='terms-conditions')
router.register(
    r'exam-pauses',
    ExamPauseViewSet,
    basename='exam-pause'
)

urlpatterns = router.urls
