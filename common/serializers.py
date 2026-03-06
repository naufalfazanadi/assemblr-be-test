from rest_framework import serializers


class StrictMixin:
    # Reject any fields in the input that are not explicitly declared
    def to_internal_value(self, data):
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {field: ['Unknown field.'] for field in sorted(unknown)}
            )
        return super().to_internal_value(data)
