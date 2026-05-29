from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Organization, OrganizationMembership, AuditLog


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "created_at", "is_active"]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ["id", "user", "organization", "role", "joined_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id", "entity_type", "entity_id", "action",
            "old_value", "new_value", "changed_by",
            "timestamp", "notes",
        ]