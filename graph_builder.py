import requests
import xml.etree.ElementTree as ET
from collections import deque


def get_nuspec_url(base_url, package, version):
    base = base_url.rstrip('/') + '/'
    return f"{base}{package.lower()}/{version}/{package.lower()}.nuspec"


def fetch_nuspec_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading nuspec from {url}: {e}")
        raise


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
                version_elem = dep.get('version')
                if id_elem:
                    # Сохраняем в формате "id:version"
                    direct_deps.add(f"{id_elem}:{version_elem or 'latest'}")
        return list(direct_deps)
    except ET.ParseError:
        print("Error: Invalid .nuspec XML format.")
        raise


def get_dependencies_real_repo(package, version, base_url):
    nuspec_url = get_nuspec_url(base_url, package, version)
    nuspec_content = fetch_nuspec_content(nuspec_url)
    deps_with_versions = parse_dependencies_from_nuspec(nuspec_content)
    return deps_with_versions  # Возвращаем ["Package:version", ...]


def get_dependencies_test_repo(package, repo_path):
    try:
        with open(repo_path, 'r') as f:
            data = f.read().strip()
    except FileNotFoundError:
        print(f"Error: Test repository file '{repo_path}' not found.")
        raise
    except Exception as e:
        print(f"Error reading test repository file: {e}")
        raise

    lines = data.splitlines()
    graph = {}
    for line in lines:
        parts = line.split(':')
        if len(parts) == 2:
            pkg, deps_str = parts[0].strip(), parts[1].strip()
            deps = [d.strip() for d in deps_str.split(',')] if deps_str else []
            graph[pkg] = deps
    return graph.get(package, [])


def build_dependency_graph(start_package, start_version, base_url, max_depth, filter_str, test_mode, repo_path=None):
    graph = {}
    visited = {}  # (package, version): depth
    queue = deque([(start_package, start_version, 0)])  # (pkg, version, depth)

    while queue:
        current_pkg, current_ver, depth = queue.popleft()

        if depth >= max_depth:
            continue

        if filter_str and filter_str in current_pkg:
            continue

        if (current_pkg, current_ver) in visited and visited[(current_pkg, current_ver)] <= depth:
            continue

        visited[(current_pkg, current_ver)] = depth

        if test_mode:
            deps = get_dependencies_test_repo(current_pkg, repo_path)
            # В тестовом режиме версии нет — используем "latest"
            for dep in deps:
                if (dep, "latest") not in visited or visited[(dep, "latest")] > depth + 1:
                    queue.append((dep, "latest", depth + 1))
        else:
            deps_with_versions = get_dependencies_real_repo(current_pkg, current_ver, base_url)
            # Преобразуем в список имён пакетов для графа
            deps = [dep.split(':')[0] for dep in deps_with_versions]
            # Добавляем в очередь с версией
            for dep_with_version in deps_with_versions:
                dep_name, dep_version = dep_with_version.split(':', 1)
                if (dep_name, dep_version) not in visited or visited[(dep_name, dep_version)] > depth + 1:
                    queue.append((dep_name, dep_version, depth + 1))

        graph[current_pkg] = deps

    return graph


def print_tree(graph, start, visited=None, prefix="", is_last=True):
    if visited is None:
        visited = set()

    print(f"{prefix}{'└── ' if is_last else '├── '}{start}")
    if start in visited:
        return

    visited.add(start)

    children = graph.get(start, [])
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(graph, child, visited.copy(), new_prefix, is_last_child)