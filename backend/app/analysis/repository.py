from __future__ import annotations

import ast
from collections import Counter, defaultdict
from datetime import UTC, datetime
import hashlib
import re
from pathlib import Path

IGNORED = {'.git', 'node_modules', 'dist', 'build', 'target', '.venv', 'venv', '__pycache__', '.idea'}
EXTENSIONS = {'.py': 'Python', '.java': 'Java'}

def _module(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    parts = relative.parts
    if len(parts) > 2 and parts[0] in {'services', 'apps', 'packages', 'modules'}:
        return parts[1]
    return parts[0] if len(parts) > 1 else root.name

def _complexity(text: str, language: str) -> int:
    if language == 'Python':
        try:
            tree = ast.parse(text)
            return 1 + sum(isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.Match, ast.comprehension)) for node in ast.walk(tree))
        except SyntaxError:
            pass
    return 1 + len(re.findall(r'\b(if|for|while|case|catch|&&|\|\|)\b', text))

def _imports(text: str, language: str) -> set[str]:
    if language == 'Python':
        return set(re.findall(r'^\s*(?:from|import)\s+([\w.]+)', text, re.MULTILINE))
    return set(re.findall(r'^\s*import\s+([\w.]+)', text, re.MULTILINE))

def analyze_repository(root: Path, name: str, branch: str = 'uploaded') -> dict:
    files = [p for p in root.rglob('*') if p.is_file() and p.suffix in EXTENSIONS and not any(part in IGNORED for part in p.parts)]
    if not files:
        raise ValueError('仓库中没有可分析的 Java 或 Python 文件。')
    if len(files) > 15000:
        raise ValueError('仓库代码文件超过 15000 个，请缩小扫描范围。')

    modules: dict[str, dict] = defaultdict(lambda: {'loc': 0, 'complexity': 0, 'files': 0, 'languages': Counter(), 'imports': set()})
    hotspots = []
    for path in files:
        language = EXTENSIONS[path.suffix]
        text = path.read_text(encoding='utf-8', errors='ignore')
        loc = sum(1 for line in text.splitlines() if line.strip())
        complexity = _complexity(text, language)
        module = _module(path, root)
        info = modules[module]
        info['loc'] += loc; info['complexity'] += complexity; info['files'] += 1
        info['languages'][language] += loc; info['imports'].update(_imports(text, language))
        hotspots.append({'path': path.relative_to(root).as_posix(), 'module': module, 'language': language,
                         'complexity': complexity, 'churn': 0, 'coverage': 0, 'authors': 0,
                         'last_changed': datetime.now(UTC).date().isoformat()})

    module_names = set(modules)
    edges_set: set[tuple[str, str]] = set()
    for source, info in modules.items():
        for imported in info['imports']:
            normalized = imported.lower().replace('_', '-')
            for target in module_names:
                if target != source and target.lower().replace('_', '-') in normalized:
                    edges_set.add((source, target))

    degrees = Counter(x for pair in edges_set for x in pair)
    nodes = []
    for module, info in modules.items():
        language = info['languages'].most_common(1)[0][0]
        avg_complexity = round(info['complexity'] / max(info['files'], 1), 1)
        risk = min(100, round(avg_complexity * 2.4 + degrees[module] * 5))
        nodes.append({'id': module, 'label': module, 'language': language, 'domain': 'repository', 'loc': info['loc'],
                      'complexity': avg_complexity, 'churn': 0, 'coverage': 0, 'risk': risk, 'degree': degrees[module]})
    nodes.sort(key=lambda item: item['loc'], reverse=True)
    edges = [{'source': s, 'target': t, 'calls': 1, 'coupling': 50, 'cyclic': (t, s) in edges_set} for s, t in sorted(edges_set)]
    cycles = [[s, t, s] for s, t in edges_set if (t, s) in edges_set and s < t]
    hotspots = sorted(hotspots, key=lambda item: item['complexity'], reverse=True)[:20]
    insights = []
    for node in sorted(nodes, key=lambda item: item['risk'], reverse=True)[:4]:
        severity = 'high' if node['risk'] >= 60 else 'medium'
        insights.append({'severity': severity, 'title': f"{node['label']} 复杂度需要关注",
                         'detail': f"该模块包含 {node['loc']:,} 行有效代码，平均文件复杂度 {node['complexity']}，连接度 {node['degree']}。",
                         'module': node['id']})
    digest = hashlib.sha1(''.join(sorted(p.as_posix() for p in files)).encode()).hexdigest()[:7]
    return {'repository': {'name': name, 'branch': branch, 'commit': digest, 'languages': dict(Counter(EXTENSIONS[p.suffix] for p in files)),
                           'synthetic': False, 'scanned_at': datetime.now(UTC).isoformat()},
            'summary': {'modules': len(nodes), 'dependencies': len(edges), 'files': len(files), 'lines': sum(n['loc'] for n in nodes),
                        'cycles': len(cycles), 'avg_complexity': round(sum(n['complexity'] for n in nodes) / len(nodes), 1), 'test_coverage': 0},
            'nodes': nodes, 'edges': edges, 'cycles': cycles, 'hotspots': hotspots, 'insights': insights}
