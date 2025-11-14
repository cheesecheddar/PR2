import os
import requests


def validate_package(value):
    if not value.strip():
        raise ValueError("package name cannot be empty.")


def validate_repo_url(value, test_mode):
    if not value.strip():
        raise ValueError("repo-url cannot be empty.")

    if test_mode:
        if not os.path.isfile(value):
            raise ValueError(f"test repository file '{value}' does not exist.")
    else:
        if not value.startswith(('http://', 'https://')):
            raise ValueError("repo-url must be a valid HTTP/HTTPS URL.")
        # Не проверяем доступность, т.к. NuGet API не отвечает на HEAD


def validate_version(value):
    if not value.strip():
        raise ValueError("version cannot be empty.")


def validate_max_depth(value):
    if value < 0:
        raise ValueError("max-depth must be a non-negative integer.")


def validate_filter(value):
    pass