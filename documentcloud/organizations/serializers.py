# Django
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

# DocumentCloud
from documentcloud.organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "avatar_url",
            "individual",
            "monthly_ai_credits",
            "name",
            "number_ai_credits",
            "slug",
            "uuid",
        ]
        extra_kwargs = {
            "avatar_url": {"read_only": True},
            "individual": {"read_only": True},
            "name": {"read_only": True},
            "slug": {"read_only": True},
        }

    def to_representation(self, instance):
        """Check if this instance should display AI credits"""
        if "monthly_ai_credits" in self.fields:
            # skip checks if we have already removed the fields
            request = self.context and self.context.get("request")
            user = request and request.user
            is_org = isinstance(instance, Organization)
            if not (
                is_org and user and user.is_authenticated and instance.has_member(user)
            ):
                # only members may see AI credits
                self.fields.pop("monthly_ai_credits")
                self.fields.pop("number_ai_credits")

        return super().to_representation(instance)


class AICreditSerializer(serializers.Serializer):
    """Serializer for the AI credit endpoint"""

    # pylint: disable=abstract-method

    ai_credits = serializers.IntegerField(
        label=_("AI Credits"),
        help_text=_("Amount of AI credits to charge to the organization"),
    )
    note = serializers.CharField(
        label=_("Note"),
        help_text=_("What are these credits being used for?"),
        max_length=1000,
        required=False,
    )
    user_id = serializers.IntegerField(label=_("User ID"), required=False)

    def validate_ai_credits(self, value):
        if value < 0:
            raise serializers.ValidationError("AI credits may not be negative")
        return value
