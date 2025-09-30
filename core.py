# core functions for envsubst-windows-linux (zero deps)
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set

# Match ${VAR} or {{VAR}} with safe variable names (A-Z, 0-9, _)
PATTERN = re.compile(r"(?:\$\{([A-Z0-9_]+)\}|{{([A-Z0-9_]+)}})")

def load_env_file(path: str) -> Dict[str, str]:
    """
    Parse a simple .env (KEY=VALUE, no complex escaping).
    - Ignores linhas começadas por '#'
    - Remove BOM se existir (usa 'utf-8-sig')
    """
    result: Dict[str, str] = {}
    p = Path(path)
    if not p.exists():
        return result

    # 'utf-8-sig' remove automaticamente o BOM (EF BB BF) se existir.
    txt = p.read_text(encoding="utf-8-sig")
    for raw in txt.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        # limpar espaços e qualquer BOM residual
        k = k.strip().lstrip("\ufeff")
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        result[k] = v
    return result

def iter_paths_with_globs(paths: Iterable[str]):
    for p in paths:
        if any(ch in p for ch in ["*", "?", "["]):
            for m in Path().glob(p):
                yield m
        else:
            yield Path(p)

def collect_files(paths: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for p in iter_paths_with_globs(paths):
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    files.append(f)
    return files

def list_missing_vars(text: str, env_map: Dict[str, str]) -> Set[str]:
    missing: Set[str] = set()
    for m in PATTERN.finditer(text):
        var = m.group(1) or m.group(2)
        if var not in env_map:
            missing.add(var)
    return missing

def substitute_text(text: str, env_map: Dict[str, str], safe: bool = False) -> str:
    def _raise_missing(var: str) -> str:
        raise KeyError(f"Missing variable: {var}")

    def repl(m):
        var = m.group(1) or m.group(2)
        if var in env_map:
            return env_map[var]
        return m.group(0) if safe else _raise_missing(var)

    return PATTERN.sub(repl, text)

def make_preview_diff(before: str, after: str, name: str) -> str:
    """Minimal diff-like preview (no colors, zero deps)."""
    b_lines = before.splitlines()
    a_lines = after.splitlines()
    out = [f"@@ {name} (preview) @@"]

    max_len = max(len(b_lines), len(a_lines))
    for i in range(max_len):
        b = b_lines[i] if i < len(b_lines) else ""
        a = a_lines[i] if i < len(a_lines) else ""
        if b != a:
            out.append(f"- {b}")
            out.append(f"+ {a}")
    if len(out) == 1:
        out.append("(no changes)")
    return "\n".join(out)
