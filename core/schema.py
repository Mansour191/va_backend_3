from graphene import relay, ObjectType, Schema, Mutation, Field, List, String, Int, Float, Boolean, DateTime, JSONString, ID
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

# Import all new schemas from api package
from api.schema import Query as APIQuery, Mutation as APIMutation

User = get_user_model()


# Authentication and Permission Mixins
class IsAuthenticatedMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()


class IsStaffMixin:
    @classmethod
    def get_queryset(cls, queryset, info):
        if info.context.user.is_authenticated and info.context.user.is_staff:
            return queryset
        return queryset.none()


# Combine all queries and mutations
class Query(APIQuery):
    """Root query combining all domain queries"""
    pass

class Mutation(APIMutation):
    """Root mutation combining all domain mutations"""
    pass

# Export schema
schema = Schema(query=Query, mutation=Mutation)
