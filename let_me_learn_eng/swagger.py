from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors.view import SwaggerAutoSchema
from drf_yasg.errors import SwaggerGenerationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg import inspectors

# ✅ 1. Safe SwaggerAutoSchema that prints errors instead of crashing
class SafeSwaggerAutoSchema(SwaggerAutoSchema):
    def get_request_body_parameters(self, consumes):
        try:
            return super().get_request_body_parameters(consumes)
        except SwaggerGenerationError as e:
            view = getattr(self.view, "__class__", self.view)
            path = getattr(self.view, "action", "unknown action")
            method = self.method
            print(f"[SwaggerGenerationError] view={view}, action={path}, method={method}: {e}")
            return []  # return empty to continue generation

# ✅ 2. Make drf_yasg use this globally
inspectors.SwaggerAutoSchema = SafeSwaggerAutoSchema

# ✅ 3. Generator supporting both HTTP and HTTPS
class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["https", "http"]
        return schema

# ✅ 4. Schema view
schema_view = get_schema_view(
    openapi.Info(
        title="letMeLearnEnglish APIs",
        default_version="v1",
        description="This document contains the APIs for letMeLearnEnglish v1",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hello@hunchhadigital.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=BothHttpAndHttpsSchemaGenerator,
    authentication_classes=(JWTAuthentication,),
)
