import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import sentry_sdk


def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment="development"
    )

def log_to_sentry(error: Exception):
    sentry_sdk.capture_exception(error)