from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import CustomPermissionClass, CustomRole
from user.permissions import HasAnyCustomPermission
from user.serializers.role_permissions_serializers import CustomRoleSerializer, RoleWithPermissionsSerializer
from utils.paginator import RolePageNumberPagination
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()

class RoleDropdownViewSet(viewsets.ViewSet):
  
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="List all roles with id and role name for dropdown",
        responses={200: openapi.Response('List of roles', openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'role': openapi.Schema(type=openapi.TYPE_STRING)
            }),
        ))}
    )
    def list(self, request, *args, **kwargs):
        try:
            roles = CustomRole.objects.all().values('id', 'role')
            return Response(roles, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f"Failed to retrieve roles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RolePermissionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    required_permissions = {
        "can_read_roles",
        "can_write_roles",
        "can_update_roles",
        "can_delete_roles"
    }

    @swagger_auto_schema(
        operation_description="List all roles or get a specific role by ID with permissions",
        manual_parameters=[
            openapi.Parameter('search_role', openapi.IN_QUERY, description="Filter roles by exact role name", type=openapi.TYPE_STRING)
        ],
        responses={200: RoleWithPermissionsSerializer(many=True)}
    )    
    @action(detail=False, methods=['get'], url_path='', url_name='list_roles')
    def list_roles(self, request, pk=None, *args, **kwargs):
        try:
            if pk:
                role = CustomRole.objects.filter(id=pk).prefetch_related('permissions').first()
                if role is None:
                    return Response(
                        {'error': 'Role not found or does not belong to the user\'s .'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                serializer = RoleWithPermissionsSerializer(role,context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            search_role = request.query_params.get("search_role")
            roles = CustomRole.objects.all().prefetch_related('permissions').order_by('id')  # Added order_by

            if search_role:
                roles = roles.filter(role__iexact=search_role)

            paginator = RolePageNumberPagination()
            paginated_roles = paginator.paginate_queryset(roles, request)  # Pass request here

            serializer = RoleWithPermissionsSerializer(paginated_roles, many=True, context={'request': request})


            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            return Response(
                {'error': f"Failed to retrieve roles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {'error': f"Failed to retrieve roles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['role_name', 'entities'],
            properties={
                'role_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the role'),
                'entities': openapi.Schema(type=openapi.TYPE_OBJECT, description='Dictionary of entities with permission flags'),
            }
        ),
        responses={201: CustomRoleSerializer()},
        operation_description="Create a new role with permissions"
    )
    @action(detail=False, methods=['post'], url_path='create', url_name='create_role')
    @transaction.atomic
    def create_role_and_permission(self, request, *args, **kwargs):
        try:
            role_name = request.data.get('role_name')
            entities = request.data.get('entities')

            if not role_name:
                return Response({'error': 'Role name is required.'}, status=status.HTTP_400_BAD_REQUEST)

            if not entities or not isinstance(entities, dict):
                return Response({'error': 'Entities object with permissions is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create Django group
            group = Group.objects.create(name=role_name)

            # Create custom role and associate group
            role = CustomRole.objects.create(role=role_name, group=group)

            for entity, actions in entities.items():
                for action, allowed in actions.items():
                    if allowed:
                        codename = f"can_{action.lower()}_{entity.lower()}"
                        permission_name = f"Can {action.capitalize()} {entity.capitalize()}"

                        # Create or get the permission
                        permission, _ = Permission.objects.get_or_create(
                            codename=codename,
                            name=permission_name,
                            content_type=ContentType.objects.get_for_model(CustomPermissionClass)
                        )

                        # Assign to group
                        group.permissions.add(permission)

                        # Create custom permission record
                        CustomPermissionClass.objects.create(name=codename, role=role)

            # Assign users (and add them to group)
            user_ids = request.data.get('users', [])
            if user_ids:
                users = User.objects.filter(id__in=user_ids)
                role.user.set(users)
                for user in users:
                    user.groups.add(group)

            role_serializer = CustomRoleSerializer(role)

            return Response(
                {
                    'status': 'Role and Permissions created successfully',
                    'role': role_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({'error': f"Failed to create role and permissions: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @swagger_auto_schema(
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'role_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the role'),
    #             'entities': openapi.Schema(type=openapi.TYPE_OBJECT, description='Dictionary of entities with permission flags'),
    #         }
    #     ),
    #     responses={200: CustomRoleSerializer()},
    #     operation_description="Update an existing role and permissions"
    # )
    @action(detail=True, methods=['put', 'patch'], url_path='update', url_name='update_role')
    @transaction.atomic
    def update_role_and_permission(self, request, *args, **kwargs):
        try:
            role_id = kwargs.get('pk')
            role = CustomRole.objects.get(id=role_id)
            group = role.group

            # Get data from request; for PATCH allow missing fields
            role_name = request.data.get('role_name', None)
            entities = request.data.get('entities', None)
            user_ids = request.data.get('users', None)

            # If PATCH and nothing provided, return error
            if request.method == 'PATCH' and not any([role_name, entities, user_ids]):
                return Response(
                    {'error': 'At least one of role_name, entities, or users must be provided.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update role name if provided and different
            if role_name and role.role != role_name:
                role.role = role_name
                if group:
                    group.name = role_name
                    group.save()
                else:
                    group = Group.objects.create(name=role_name)
                    role.group = group
                role.save()

            # Update permissions only if entities provided
            if entities is not None:
                if not isinstance(entities, dict):
                    return Response(
                        {'error': 'Entities must be provided as a dictionary.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Clear old permissions for the role
                CustomPermissionClass.objects.filter(role=role).delete()
                if group:
                    group.permissions.clear()

                # Create new permissions and assign to group
                for entity, actions in entities.items():
                    for action, allowed in actions.items():
                        if allowed:
                            codename = f"can_{action.lower()}_{entity.lower()}"
                            permission_name = f"Can {action.capitalize()} {entity.capitalize()}"

                            permission, _ = Permission.objects.get_or_create(
                                codename=codename,
                                name=permission_name,
                                content_type=ContentType.objects.get_for_model(CustomPermissionClass)
                            )

                            if group:
                                group.permissions.add(permission)

                            CustomPermissionClass.objects.create(name=codename, role=role)

            # Update users only if user_ids provided
            if user_ids is not None:
                users = User.objects.filter(id__in=user_ids)
                role.user.set(users)
                for user in users:
                    if group:
                        user.groups.add(group)

            role_serializer = CustomRoleSerializer(role)
            return Response(
                {
                    'status': 'Role and Permissions updated successfully',
                    'role': role_serializer.data,
                },
                status=status.HTTP_200_OK
            )

        except CustomRole.DoesNotExist:
            return Response({'error': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"Failed to update role and permissions: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @swagger_auto_schema(
        responses={204: 'Role deleted successfully'},
        operation_description="Delete an existing role"
    )
    @action(detail=True, methods=['delete'], url_path='delete', url_name='delete_role')
    @transaction.atomic
    def delete_role(self, request, *args, **kwargs):
        try:
            role_id = kwargs.get('pk')
            role = CustomRole.objects.get(id=role_id)

            # Optionally delete group
            if role.group:
                role.group.delete()

            role.delete()

            return Response({'status': 'Role deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except CustomRole.DoesNotExist:
            return Response({'error': 'Role not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"Failed to delete role: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @swagger_auto_schema(
        methods=['delete'],
        manual_parameters=[
            openapi.Parameter(
                'permission_id', openapi.IN_QUERY, 
                description="ID of the permission to delete", 
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={204: 'Permission deleted successfully', 404: 'Permission not found'}
    )
    @action(detail=False, methods=['delete'], url_path='delete_permission', url_name='delete_permission')
    @transaction.atomic
    def delete_permission(self, request, *args, **kwargs):
        permission_id = request.query_params.get('permission_id')
        if not permission_id:
            return Response(
                {'error': 'permission_id query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permission = CustomPermissionClass.objects.get(id=permission_id)
            permission.delete()
            return Response({'status': 'Permission deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except CustomPermissionClass.DoesNotExist:
            return Response({'error': 'Permission not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Failed to delete permission: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
