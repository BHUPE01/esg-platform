from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    """
    Represents a client/tenant on the platform.
    Every piece of data is scoped to an org.
    """
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """
    Links a Django User to an Organization with a role.
    Simple RBAC: admin can manage, analyst can review.
    """
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("viewer", "Viewer"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="analyst")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "organization")

    def __str__(self):
        return f"{self.user.username} @ {self.organization.name} ({self.role})"


class AuditLog(models.Model):
    """
    Immutable record of every meaningful change in the system.
    Written once, never updated or deleted.

    - entity_type: which model changed (e.g. 'NormalizedRecord')
    - entity_id:   the PK of the changed object
    - action:      what happened (created, updated, approved, rejected, etc.)
    - old_value:   JSON snapshot BEFORE the change
    - new_value:   JSON snapshot AFTER the change
    - changed_by:  who did it
    - timestamp:   when it happened
    - organization: which tenant
    """
    ACTION_CHOICES = [
        ("created", "Created"),
        ("updated", "Updated"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("flagged", "Flagged"),
        ("normalized", "Normalized"),
        ("ingested", "Ingested"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="audit_logs"
    )
    entity_type = models.CharField(max_length=100)
    entity_id = models.BigIntegerField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["organization", "-timestamp"]),
        ]

    def __str__(self):
        return f"[{self.action}] {self.entity_type} #{self.entity_id} by {self.changed_by}"


def write_audit_log(*, organization, entity_type, entity_id, action,
                    old_value=None, new_value=None, changed_by=None, notes=""):
    """
    Convenience function — call this from anywhere in the codebase
    to write an audit entry. Keeps audit writes consistent.
    """
    AuditLog.objects.create(
        organization=organization,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        changed_by=changed_by,
        notes=notes,
    )