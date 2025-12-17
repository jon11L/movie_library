from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files (CSS, JS, etc.)"""
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME_STATIC
    location = 'static'
    file_overwrite = True
    default_acl = None


class MediaStorage(S3Boto3Storage):
    """Storage backend for media files (user upload)"""
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME_MEDIA
    location = 'media'
    default_acl = None
    file_overwrite = False
