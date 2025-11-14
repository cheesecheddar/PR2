import argparse
import sys


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

    # package: не может быть пустым
    if not args.package.strip():
        errors.append("Error: package name cannot be empty.")

    # repo-url: не может быть пустым
    if not args.repo_url.strip():
        errors.append("Error: repo-url cannot be empty.")

    # max-depth: должен быть неотрицательным
    if args.max_depth < 0:
        errors.append("Error: max-depth must be a non-negative integer.")

    # version: не может быть пустой строкой
    if not args.version.strip():
        errors.append("Error: version cannot be empty.")

    # filter: проверим, что он строка (всегда True в Python, но добавим для симметрии)
    # на самом деле, фильтр может быть пустым — это нормально.

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)


def main():
    try:
        args = parse_args()
    except SystemExit:
        print("Error: Invalid command-line arguments.")
        sys.exit(1)

    validate_args(args)

    print("=== Configuration ===")
    print(f"package: {args.package}")
    print(f"repo_url: {args.repo_url}")
    print(f"test_mode: {args.test_mode}")
    print(f"version: {args.version}")
    print(f"output_tree: {args.output_tree}")
    print(f"max_depth: {args.max_depth}")
    print(f"filter: {args.filter}")
    print("=====================")

    print("Configuration is valid.")


if __name__ == "__main__":
    main()