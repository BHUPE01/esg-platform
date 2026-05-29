from django.contrib import admin
from .models import Organization, OrganizationMembership, AuditLog


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "role", "joined_at"]
    list_filter = ["role", "organization"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["entity_type", "entity_id", "action", "changed_by", "timestamp"]
    list_filter = ["action", "entity_type"]
    readonly_fields = ["entity_type", "entity_id", "action", "old_value",
                       "new_value", "changed_by", "timestamp"]
    # Audit logs must NEVER be editable in admin either
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False