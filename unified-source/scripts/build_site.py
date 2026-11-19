#!/usr/bin/env python3
"""Build the shared TP26 static study portal and per-subject data bundles."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import unicodedata
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VAULT = Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Учеба"
IMAGE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}
CATEGORY_ORDER = ["Лекции", "Практики", "Разборы", "Справочник", "Экзамен", "Билеты", "Архив", "Домашние задания", "Задачи", "Конспекты", "Обзор"]


def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def normalize_heading(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    value = re.sub(r"\\[a-zA-Z]+", "", value)
    return "".join(ch for ch in value if unicodedata.category(ch)[0] in {"L", "N"})


def strip_todo_callouts(content: str) -> str:
    """Remove authoring-only TODO callouts without changing surrounding material."""
    return re.sub(r"^>\s*\[!todo\][^\n]*\n(?:>.*(?:\n|$))*", "", content, flags=re.IGNORECASE | re.MULTILINE)


def category_for(subject_id: str, rel: str) -> str:
    parts = PurePosixPath(rel).parts
    if "Разборы" in parts:
        return "Разборы"
    if subject_id == "matan":
        if rel.startswith("Лекции/"):
            return "Лекции"
        if rel.startswith("Практики/Разборы/"):
            return "Разборы"
        if rel.startswith("Практики/"):
            return "Практики"
        if rel.startswith("Справочник/"):
            return "Справочник"
        if "Экзамен — подготовка/" in rel:
            return "Экзамен"
        if "Первый коллоквиум - архив/" in rel:
            return "Архив"
        return "Обзор"
    if len(parts) == 1:
        return "Обзор"
    folder = parts[0]
    low = folder.casefold()
    if "архив" in low:
        return "Архив"
    if "экзамен" in low:
        return "Экзамен"
    if "билет" in low:
        return "Билеты"
    return folder


def hidden_doc(subject_id: str, subject_title: str, rel: str, title: str) -> bool:
    parts = PurePosixPath(rel).parts
    if any(part.startswith(".") for part in parts):
        return True
    if "Разборы" in parts:
        return True
    title_key = normalize_heading(title)
    subject_key = normalize_heading(subject_title)
    if title_key == subject_key or title.startswith("00 — Карта"):
        return True
    if title in {"Лекции по матану", "Практики по матану", "Справочник по матану", "Разборы", "99 — Источники карточек"}:
        return True
    if title.startswith(("Лекции по ", "Практики по ", "Справочник по ")):
        return True
    if subject_id == "matan":
        return (
            "99 — Источники карточек" in rel
            or rel.startswith("Практики/Разборы/")
            or ("Экзамен — подготовка/" in rel and title == "00 — Карта экзамена")
            or rel.endswith("Первый коллоквиум - архив/Локальные пометки.md")
            or title == "00 — Карта коллоквиума"
        )
    return False


def resolve_doc(target: str, docs: list[dict], by_title: dict[str, list[dict]]) -> dict | None:
    target = nfc(target.split("#", 1)[0].replace("\\", "/")).strip()
    target = target.removesuffix(".md")
    parts = target.split("/")
    if len(parts) > 1:
        for index in range(len(parts) - 1):
            suffix = "/".join(parts[index:])
            matches = [doc for doc in docs if doc["path"][:-3] == suffix or doc["path"][:-3].endswith("/" + suffix)]
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                return None
        return None
    matches = by_title.get(nfc(target), [])
    return matches[0] if len(matches) == 1 else None


def normalize_relative(path: str) -> str:
    stack: list[str] = []
    for part in path.replace("\\", "/").split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(nfc(part))
    return "/".join(stack)


def resolve_asset(target: str, doc_path: str, subject_dir: str, asset_paths: set[str]) -> str | None:
    target = nfc(target.split("|", 1)[0].replace("\\", "/")).strip()
    if target.startswith("/"):
        target = target[1:]
    prefix = nfc(subject_dir) + "/"
    if target.startswith(prefix):
        target = target[len(prefix):]
    parent = str(PurePosixPath(doc_path).parent)
    candidates = [normalize_relative(f"{parent}/{target}"), normalize_relative(target)]
    for candidate in candidates:
        if candidate in asset_paths:
            return candidate
    basename = PurePosixPath(target).name
    matches = [path for path in asset_paths if PurePosixPath(path).name == basename]
    if len(matches) == 1:
        return matches[0]
    def asset_key(value: str) -> str:
        return "".join(ch for ch in nfc(value).casefold() if ch.isalnum())
    alias_matches = [path for path in asset_paths if asset_key(PurePosixPath(path).stem) == asset_key(re.sub(r"^lecture-\d+-", "", PurePosixPath(target).stem, flags=re.IGNORECASE))]
    return alias_matches[0] if len(alias_matches) == 1 else None


def validate_subject(subject: dict, docs: list[dict], all_docs: list[dict], vault: Path) -> tuple[list[str], int, int, set[str]]:
    issues: list[str] = []
    by_title: dict[str, list[dict]] = {}
    for doc in docs:
        by_title.setdefault(nfc(doc["title"]), []).append(doc)
    source = vault / subject["directory"]
    asset_paths = {
        nfc(path.relative_to(source).as_posix())
        for path in source.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    }
    embedded_count = 0
    asset_count = 0
    referenced_assets: set[str] = set()
    for doc in docs:
        content = doc["content"]
        for match in re.finditer(r"!\[\[([\s\S]*?)\]\]", content):
            spec = match.group(1)
            target, _, anchor = spec.partition("#")
            raw_target = target.split("|", 1)[0].strip()
            if PurePosixPath(raw_target).suffix.lower() in IMAGE_EXTENSIONS:
                asset_count += 1
                resolved = resolve_asset(target, doc["path"], subject["directory"], asset_paths)
                if not resolved:
                    issues.append(f"{doc['path']}: missing image {raw_target!r}")
                else:
                    referenced_assets.add(resolved)
                continue
            embedded_count += 1
            linked = resolve_doc(target, docs, by_title)
            if linked is None:
                withheld_target = nfc(target.replace("\\", "/").removesuffix(".md"))
                withheld = subject.get("withheldDocs", [])
                if any(
                    nfc(item["title"]) == withheld_target
                    or nfc(item["path"].removesuffix(".md")) == withheld_target
                    or nfc(item["path"].removesuffix(".md")).endswith("/" + withheld_target)
                    for item in withheld
                ):
                    continue
                # Cross-subject links are supported as document links, but embeds need a local bundle.
                linked = resolve_doc(target, all_docs, {})
                if linked is not None:
                    issues.append(f"{doc['path']}: cross-subject embed {target!r} is unsupported")
                    continue
                issues.append(f"{doc['path']}: missing or ambiguous target {target!r}")
                continue
            if not anchor:
                continue
            lines = linked["content"].splitlines()
            if anchor.startswith("^"):
                found = any(line.strip() == anchor for line in lines)
            else:
                wanted = normalize_heading(anchor)
                found = any(
                    re.match(r"^#{1,6}\s+", line)
                    and normalize_heading(re.sub(r"^#{1,6}\s+", "", line)) == wanted
                    for line in lines
                )
            if not found:
                issues.append(f"{doc['path']}: missing section {anchor!r} in {linked['path']}")
    return issues, embedded_count, asset_count, referenced_assets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", type=Path, default=Path(__import__("os").environ.get("STUDY_VAULT", str(DEFAULT_VAULT))))
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    vault, out = args.vault.expanduser().resolve(), args.out.resolve()
    config = json.loads((ROOT / "scripts/subjects.json").read_text(encoding="utf-8"))
    if not vault.is_dir():
        raise SystemExit(f"Vault not found: {vault}")
    subjects = []
    all_docs = []
    collected = {}
    for meta in config:
        source = vault / meta["directory"]
        if not source.is_dir():
            raise SystemExit(f"Subject folder not found: {source}")
        docs = []
        withheld = []
        excluded_paths = {nfc(item) for item in meta.get("excludePaths", [])}
        for path in sorted(source.rglob("*.md")):
            rel = nfc(path.relative_to(source).as_posix())
            if any(part.startswith(".") for part in PurePosixPath(rel).parts):
                continue
            title = nfc(path.stem)
            # Incomplete notes named "to do" and explicitly excluded source notes
            # are withheld from the public bundle; keep only metadata for safe links.
            if rel in excluded_paths:
                withheld.append({"path": rel, "title": title})
                continue
            if re.search(r"\bto\s*do\b|\btodo\b", title, re.IGNORECASE):
                continue
            doc = {"id": rel, "path": rel, "title": title, "category": category_for(meta["id"], rel),
                   "hidden": hidden_doc(meta["id"], meta["title"], rel, title),
                   "content": strip_todo_callouts(path.read_text(encoding="utf-8"))}
            docs.append(doc)
        collected[meta["id"]] = docs
        meta["withheldDocs"] = withheld
        all_docs.extend(docs)
    errors = []
    referenced_assets = {}
    for meta in config:
        issues, embeds, images, assets = validate_subject(meta, collected[meta["id"]], all_docs, vault)
        referenced_assets[meta["id"]] = assets
        errors.extend(f"{meta['id']}: {issue}" for issue in issues)
        cats = [name for name in CATEGORY_ORDER if any(d["category"] == name and not d["hidden"] for d in collected[meta["id"]])]
        cats += [name for name in dict.fromkeys(d["category"] for d in collected[meta["id"]] if not d["hidden"]) if name not in cats]
        public_meta = {key: value for key, value in meta.items() if key not in {"excludePaths", "withheldDocs"}}
        subjects.append({**public_meta, "categories": cats, "documents": len(collected[meta["id"]]),
                         "visible": sum(not d["hidden"] for d in collected[meta["id"]]),
                         "documentsIndex": [{"path": d["path"], "title": d["title"], "hidden": d["hidden"]}
                                            for d in collected[meta["id"]]]})
        print(f"{meta['id']}: {len(collected[meta['id']])} documents, {sum(not d['hidden'] for d in collected[meta['id']])} visible, {embeds} embeds, {images} images")
    if errors:
        raise SystemExit("Content validation failed:\n" + "\n".join(errors[:200]) + (f"\n… and {len(errors)-200} more" if len(errors) > 200 else ""))

    if out.exists():
        shutil.rmtree(out)
    (out / "unified-assets").mkdir(parents=True)
    (out / "unified-data").mkdir()
    template = (ROOT / "src/index.template.html").read_text(encoding="utf-8")
    style = (ROOT / "src/style.css").read_text(encoding="utf-8")
    renderer = (ROOT / "src/renderer.js").read_text(encoding="utf-8")
    runtime = (ROOT / "src/runtime.js").read_text(encoding="utf-8")
    (out / "unified-assets/style.css").write_text(style, encoding="utf-8")
    (out / "unified-assets/app.js").write_text(runtime.replace("/* RENDERER */", renderer), encoding="utf-8")
    (out / "subjects.json").write_text(json.dumps(subjects, ensure_ascii=False), encoding="utf-8")
    (out / "index.html").write_text(template.replace("__BASE__", "./").replace("__SUBJECT__", "").replace("__PORTAL__", "./"), encoding="utf-8")
    for subject in subjects:
        source = vault / subject["directory"]
        bundle_assets = []
        for rel in sorted(referenced_assets[subject["id"]]):
            path = source / rel
            dest = out / "unified-assets" / subject["id"] / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            bundle_assets.append(rel)
        payload_subject = {key: value for key, value in subject.items() if key not in {"withheldDocs", "status"}}
        payload = {"subject": payload_subject, "docs": collected[subject["id"]], "assets": bundle_assets}
        (out / "unified-data" / f"{subject['id']}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        route = out / subject["id"]
        route.mkdir()
        (route / "index.html").write_text(template.replace("__BASE__", "../").replace("__SUBJECT__", subject["id"]).replace("__PORTAL__", "../"), encoding="utf-8")
    total_docs = sum(len(v) for v in collected.values())
    print(json.dumps({"subjects": len(subjects), "documents": total_docs, "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
