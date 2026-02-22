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
    def get_operation(self, operation_keys=None):
        try:
            return super().get_operation(operation_keys)
        except Exception as e:
            # This captures the view name, the path, and the method
            view_class = getattr(self.view, "__class__", self.view)
            method = self.method
            path = getattr(self.view, "request", None)
            path_info = getattr(path, "path", "unknown") if path else "unknown"
            
            print("\n" + "="*60)
            print("❌ SWAGGER ERROR DETECTED")
            print(f"VIEW CLASS: {view_class}")
            print(f"METHOD:     {method}")
            print(f"PATH:       {path_info}")
            print(f"ERROR:      {str(e)}")
            print("="*60 + "\n")
            
            # Return None so Swagger skips this one broken endpoint 
            # instead of crashing the whole JSON file
            return None
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
