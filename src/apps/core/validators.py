from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx']
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
ALLOWED_FILE_EXTENSIONS = ALLOWED_DOCUMENT_EXTENSIONS + ALLOWED_IMAGE_EXTENSIONS
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Signatures MIME (magic bytes) pour les types autorisés
_MIME_SIGNATURES = [
    (b'%PDF', 'pdf'),
    (b'\xff\xd8\xff', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'png'),
    # ZIP-based Office formats (docx, xlsx, pptx)
    (b'PK\x03\x04', 'docx'),
    # Legacy Office (doc, xls, ppt)
    (b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1', 'doc'),
]


def _detect_mime_type(file) -> str:
    """Détecte le type réel du fichier par ses magic bytes."""
    file.seek(0)
    header = file.read(16)
    file.seek(0)
    for signature, mime_type in _MIME_SIGNATURES:
        if header.startswith(signature):
            return mime_type
    return ''


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


@deconstructible
class MimeTypeValidator:
    """Vérifie le type réel du fichier via ses magic bytes (indépendant de l'extension déclarée)."""
    def __init__(self, allowed_extensions=None):
        self.allowed_extensions = allowed_extensions or ALLOWED_FILE_EXTENSIONS

    def __call__(self, value):
        detected = _detect_mime_type(value)
        # Si le type est détectable, on vérifie qu'il correspond aux extensions autorisées
        if detected and detected not in self.allowed_extensions:
            raise ValidationError(
                f"Type de fichier refusé. Le contenu réel du fichier ({detected}) "
                f"ne correspond pas aux types autorisés : {', '.join(self.allowed_extensions)}."
            )

    def __eq__(self, other):
        return isinstance(other, MimeTypeValidator) and self.allowed_extensions == other.allowed_extensions


def validate_upload(file, allowed_extensions=None):
    """Valide extension, taille et type MIME d'un fichier uploadé."""
    FileExtensionValidator(allowed_extensions)(file)
    FileSizeValidator()(file)
    MimeTypeValidator(allowed_extensions)(file)
