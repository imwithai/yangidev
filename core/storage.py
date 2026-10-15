import os
import mimetypes
from io import BytesIO
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from django.conf import settings

@deconstructible
class DatabaseStorage(Storage):
    def _save(self, name, content):
        from .models import DatabaseMediaFile
        content_type, _ = mimetypes.guess_type(name)
        if not content_type:
            content_type = 'application/octet-stream'

        # Read the raw binary content without modification
        file_content = content.read()

        # Save or update the file in the database
        DatabaseMediaFile.objects.update_or_create(
            name=name,
            defaults={
                'content': file_content,
                'content_type': content_type
            }
        )
        return name

    def _open(self, name, mode='rb'):
        from .models import DatabaseMediaFile
        try:
            db_file = DatabaseMediaFile.objects.get(name=name)
            return ContentFile(db_file.content, name=name)
        except DatabaseMediaFile.DoesNotExist:
            return None

    def exists(self, name):
        from .models import DatabaseMediaFile
        return DatabaseMediaFile.objects.filter(name=name).exists()

    def size(self, name):
        from .models import DatabaseMediaFile
        try:
            db_file = DatabaseMediaFile.objects.get(name=name)
            return len(db_file.content)
        except DatabaseMediaFile.DoesNotExist:
            return 0

    def url(self, name):
        return os.path.join(settings.MEDIA_URL, name)

    def get_available_name(self, name, max_length=None):
        return name

    def delete(self, name):
        from .models import DatabaseMediaFile
        DatabaseMediaFile.objects.filter(name=name).delete()
