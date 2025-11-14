import argparse
import sys
import requests
import xml.etree.ElementTree as ET
from validators import (
    validate_package, validate_repo_url, validate_version,
    validate_max_depth, validate_filter
)


def parse_args():
    parser = argparse.ArgumentParser(description="GraphViz Tool for Package Dependencies")
    parser.add_argument("--package", required=True, help="Name of the package to analyze")
    parser.add_argument("--repo-url", required=True, help="URL of the repository or path to test repo")
    parser.add_argument("--test-mode", action="store_true", help="Enable test mode")
    parser.add_argument("--version", default="latest", help="Version of the package")
    parser.add_argument("--output-tree", action="store_true", help="Output dependencies in ASCII tree format")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum depth of dependency analysis")
    parser.add_argument("--filter", default="", help="Substring to filter out packages")

    return parser.parse_args()


def validate_args(args):
    errors = []
    try:
        validate_package(args.package)
    except ValueError as e:
        errors.append(f"Error: {e}")

    try:
        validate_repo_url(args.repo_url, args.test_mode)
    except ValueError as e:
        errors.append(f"Error: {e}")

    try:
        validate_version(args.version)
    except ValueError as e:
        errors.append(f"Error: {e}")

    try:
        validate_max_depth(args.max_depth)
    except ValueError as e:
        errors.append(f"Error: {e}")

    try:
        validate_filter(args.filter)
    except ValueError as e:
        errors.append(f"Error: {e}")

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)


def get_nuspec_url(base_url, package, version):
    # Убедимся, что base_url заканчивается на /
    base = base_url.rstrip('/') + '/'
    return f"{base}{package.lower()}/{version}/{package.lower()}.nuspec"


def fetch_nuspec_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading nuspec from {url}: {e}")
        sys.exit(1)


def parse_dependencies_from_nuspec(nuspec_content):
    try:
        root = ET.fromstring(nuspec_content)
        ns = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
        deps = root.find('.//ns:dependencies', ns)
        if deps is None:
            return []

        direct_deps = set()  # Используем set, чтобы избежать дубликатов
        for group in deps:
            for dep in group:
                id_elem = dep.get('id')
                if id_elem:
                    direct_deps.add(id_elem)

        return list(direct_deps)
    except ET.ParseError:
        print("Error: Invalid .nuspec XML format.")
        sys.exit(1)

def main():
    try:
        args = parse_args()
    except SystemExit:
        print("Error: Invalid command-line arguments.")
        sys.exit(1)

    validate_args(args)

    if args.test_mode:
        print("Test mode is enabled. This stage does not support test mode.")
        sys.exit(1)

    # (только для этого этапа) Вывести на экран все прямые зависимости
    nuspec_url = get_nuspec_url(args.repo_url, args.package, args.version)
    nuspec_content = fetch_nuspec_content(nuspec_url)
    dependencies = parse_dependencies_from_nuspec(nuspec_content)

    print("Direct dependencies:")
    for dep in dependencies:
        print(f"- {dep}")


if __name__ == "__main__":
    main()