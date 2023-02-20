def traceback_name(error: Exception) -> str:
    """Get traceback class names from an exception

    Args:
        error: Exception object.

    Returns:
        Exception traceback class names.
    """
    module = error.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return error.__class__.__name__
    return module + "." + error.__class__.__name__


class TorProxyException(Exception):
    "Exception raised for errors in the Tor proxy. This might happen if the Tor Service is running but the application is using a different port."
    error_code = 69


class TorServiceException(Exception):
    "Exception raised for errors in the Tor Service. This error is raised if the Tor Service is not running."
    error_code = 96
