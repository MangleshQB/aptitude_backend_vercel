def silky_custom_intercept(request):
    """Custom function to determine which requests Silk should intercept"""
    ignored_paths = [
        '/admin/',
        '/silk/',
        '/static/',
        '/media/',
        '/favicon.ico',
    ]

    for path in ignored_paths:
        if request.path.startswith(path):
            return False

    return True
