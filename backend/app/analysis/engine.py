from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
import random

MODULES = [
    ("gateway", "Java", "platform"), ("identity", "Java", "security"),
    ("order", "Java", "commerce"), ("payment", "Java", "commerce"),
    ("inventory", "Java", "supply"), ("pricing", "Python", "commerce"),
    ("recommendation", "Python", "intelligence"), ("feature-store", "Python", "intelligence"),
    ("event-bus", "Java", "platform"), ("notification", "Python", "engagement"),
    ("customer", "Java", "commerce"), ("risk", "Python", "security"),
    ("reporting", "Python", "data"), ("data-contracts", "Python", "data"),
    ("scheduler", "Java", "platform"), ("observability", "Python", "platform"),
    ("shared-kernel", "Java", "platform"), ("legacy-adapter", "Java", "integration"),
]

EDGE_PAIRS = [
    ("gateway", "identity"), ("gateway", "order"), ("gateway", "customer"),
    ("order", "payment"), ("order", "inventory"), ("order", "pricing"),
    ("payment", "risk"), ("payment", "event-bus"), ("inventory", "event-bus"),
    ("pricing", "recommendation"), ("recommendation", "feature-store"),
    ("feature-store", "data-contracts"), ("reporting", "data-contracts"),
    ("event-bus", "notification"), ("event-bus", "reporting"),
    ("notification", "customer"), ("scheduler", "reporting"),
    ("scheduler", "inventory"), ("observability", "event-bus"),
    ("legacy-adapter", "order"), ("legacy-adapter", "shared-kernel"),
    ("order", "shared-kernel"), ("payment", "shared-kernel"),
    ("inventory", "shared-kernel"), ("shared-kernel", "identity"),
    # intentional architectural cycles
    ("identity", "gateway"), ("risk", "payment"), ("data-contracts", "reporting"),
]

def find_cycles(edges: list[tuple[str, str]]) -> list[list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for source, target in edges:
        graph[source].append(target)
    found: set[tuple[str, ...]] = set()

    def walk(node: str, path: list[str], active: set[str]) -> None:
        for nxt in graph[node]:
            if nxt in active:
                cycle = path[path.index(nxt):] + [nxt]
                core = cycle[:-1]
                rotations = [tuple(core[i:] + core[:i]) for i in range(len(core))]
                found.add(min(rotations))
            elif len(path) < 8:
                walk(nxt, path + [nxt], active | {nxt})

    for node in list(graph):
        walk(node, [node], {node})
    return [list(cycle) + [cycle[0]] for cycle in sorted(found)]

def build_snapshot(seed: int = 20260817) -> dict:
    rng = random.Random(seed)
    degrees = Counter()
    for source, target in EDGE_PAIRS:
        degrees[source] += 1
        degrees[target] += 1
    risky = {"payment", "shared-kernel", "legacy-adapter", "reporting"}
    nodes = []
    files = []
    for index, (name, language, domain) in enumerate(MODULES):
        loc = rng.randint(1400, 9400)
        complexity = rng.randint(18, 62) + (28 if name in risky else 0)
        churn = rng.randint(4, 31) + (24 if name in risky else 0)
        coverage = rng.randint(63, 94) - (22 if name in risky else 0)
        risk = min(100, round(complexity * .47 + churn * .58 + (100 - coverage) * .36))
        nodes.append({"id": name, "label": name, "language": language, "domain": domain,
                      "loc": loc, "complexity": complexity, "churn": churn,
                      "coverage": coverage, "risk": risk, "degree": degrees[name]})
        for item in range(3):
            file_complexity = max(4, complexity + rng.randint(-14, 18))
            file_churn = max(1, churn + rng.randint(-10, 15))
            files.append({"path": f"services/{name}/src/{name.replace('-', '_')}_{['service','handler','repository'][item]}.{'py' if language == 'Python' else 'java'}",
                          "module": name, "language": language, "complexity": file_complexity,
                          "churn": file_churn, "coverage": max(18, min(99, coverage + rng.randint(-12, 9))),
                          "authors": rng.randint(1, 7), "last_changed": f"2026-08-{rng.randint(1,16):02d}"})
    cycles = find_cycles(EDGE_PAIRS)
    cycle_edges = {(cycle[i], cycle[i + 1]) for cycle in cycles for i in range(len(cycle) - 1)}
    edges = [{"source": s, "target": t, "calls": rng.randint(18, 860),
              "coupling": rng.randint(25, 94), "cyclic": (s, t) in cycle_edges} for s, t in EDGE_PAIRS]
    hotspots = sorted(files, key=lambda f: f["complexity"] * .55 + f["churn"] * .7 - f["coverage"] * .2, reverse=True)[:10]
    return {
        "repository": {"name": "nimbus-commerce", "branch": "main", "commit": "7f3ac91",
                       "languages": {"Java": 57, "Python": 36, "SQL": 7}, "synthetic": True,
                       "scanned_at": datetime.now(UTC).isoformat()},
        "summary": {"modules": len(nodes), "dependencies": len(edges), "files": len(files),
                    "lines": sum(n["loc"] for n in nodes), "cycles": len(cycles),
                    "avg_complexity": round(sum(n["complexity"] for n in nodes) / len(nodes), 1),
                    "test_coverage": round(sum(n["coverage"] for n in nodes) / len(nodes), 1)},
        "nodes": nodes, "edges": edges, "cycles": cycles, "hotspots": hotspots,
        "insights": [
            {"severity": "critical", "title": "支付与风控形成双向依赖", "detail": "payment ↔ risk 阻碍独立发布，建议通过风险决策端口反转依赖。", "module": "payment"},
            {"severity": "high", "title": "shared-kernel 正在成为变更放大器", "detail": "4 个核心服务直接依赖共享内核，近期变更频率与扇入同时升高。", "module": "shared-kernel"},
            {"severity": "high", "title": "legacy-adapter 测试防线不足", "detail": "高复杂度与低覆盖率重叠，建议先建立契约测试再拆分适配层。", "module": "legacy-adapter"},
            {"severity": "medium", "title": "报表契约边界不清晰", "detail": "reporting 与 data-contracts 互相引用，应将共享 schema 下沉为只读契约包。", "module": "reporting"},
        ],
    }
