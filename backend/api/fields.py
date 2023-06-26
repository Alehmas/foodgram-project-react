import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class ImageConversion(serializers.Field):
    """Serialization for image field in recipe."""

    def to_representation(self, value):
        return value.url

    def to_internal_value(self, data):
        try:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = "image." + ext
            return ContentFile(base64.b64decode(imgstr), name=file_name)
        except ValueError:
            raise serializers.ValidationError(
                'Image must be base64 encoded'
            )
