class AuthError(Exception):
    "Raised on OAuth or credential errors."

class ServiceError(Exception):
    "Raised on Gmail API call failures."

class AttachmentError(Exception):
    "Raised when attachment download or decryption fails."