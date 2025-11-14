import argparse
import sys
from validators import (
    validate_package, validate_repo_url, validate_version,
    validate_max_depth, validate_filter
)
from graph_builder import build_dependency_graph, print_tree


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


def main():
    try:
        args = parse_args()
    except SystemExit:
        print("Error: Invalid command-line arguments.")
        sys.exit(1)

    validate_args(args)

    if args.test_mode:
        repo_path = args.repo_url
        graph = build_dependency_graph(
            args.package, args.version, "", args.max_depth, args.filter, test_mode=True, repo_path=repo_path
        )
        print("Graph built from test repository:")
        for pkg, deps in graph.items():
            print(f"{pkg}: {deps}")
        if args.output_tree:
            print("Dependency Tree (Test Mode):")
            print_tree(graph, args.package)
    else:
        graph = build_dependency_graph(
            args.package, args.version, args.repo_url, args.max_depth, args.filter, test_mode=False
        )
        if args.output_tree:
            print("Dependency Tree (Real Mode):")
            print_tree(graph, args.package)
        else:
            print("Graph built successfully.")
            for pkg, deps in graph.items():
                print(f"{pkg}: {deps}")


if __name__ == "__main__":
    main()