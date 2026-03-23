import os
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] is filename, [1] is extension
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

def validate_file_size(value):
    filesize = value.size
    if filesize > 5242880: # 5MB limit
        raise ValidationError("The maximum file size that can be uploaded is 5MB")