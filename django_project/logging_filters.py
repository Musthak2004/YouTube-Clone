import logging


class IgnoreHttpsProbeFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        blocked_messages = (
            "You're accessing the development server over HTTPS, but it only supports HTTP.",
            "Bad request version",
        )
        return not any(item in message for item in blocked_messages)
