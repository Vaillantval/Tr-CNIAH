from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx']
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
ALLOWED_FILE_EXTENSIONS = ALLOWED_DOCUMENT_EXTENSIONS + ALLOWED_IMAGE_EXTENSIONS
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@deconstructible
class FileExtensionValidator:
    def __init__(self, allowed_extensions=None):
        self.allowed_extensions = allowed_extensions or ALLOWED_FILE_EXTENSIONS

    def __call__(self, value):
        ext = value.name.rsplit('.', 1)[-1].lower() if '.' in value.name else ''
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Extension non autorisée : .{ext}. "
                f"Extensions acceptées : {', '.join(self.allowed_extensions)}."
            )

    def __eq__(self, other):
        return isinstance(other, FileExtensionValidator) and self.allowed_extensions == other.allowed_extensions


@deconstructible
class FileSizeValidator:
    def __init__(self, max_size_bytes=MAX_FILE_SIZE_BYTES):
        self.max_size_bytes = max_size_bytes

    def __call__(self, value):
        if value.size > self.max_size_bytes:
            max_mb = self.max_size_bytes / (1024 * 1024)
            raise ValidationError(
                f"Fichier trop volumineux. Taille maximale autorisée : {max_mb:.0f} Mo."
            )

    def __eq__(self, other):
        return isinstance(other, FileSizeValidator) and self.max_size_bytes == other.max_size_bytes


def validate_upload(file, allowed_extensions=None):
    FileExtensionValidator(allowed_extensions)(file)
    FileSizeValidator()(file)
