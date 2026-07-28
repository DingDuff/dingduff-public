#!/usr/bin/env python3
"""Validate skill frontmatter and packaged .skill artifacts.

A malformed `description:` in SKILL.md frontmatter makes Claude Code skip the
skill with no error at all — the skill count just drops (issue #35). These
checks turn that silent failure into a loud one.

Checks:
  1. Every plugins/*/skills/*/SKILL.md has frontmatter that parses as YAML and
     carries `name` and `description`.
  2. Every dist/*.skill bundles a SKILL.md byte-identical to its source, so a
     source fix can't ship with a stale zip.
  3. The `(vX.Y.Z)` tag in each description matches the dist filename version.

Run locally with: python3 scripts/validate_skills.py
"""

import glob
import os
import re
import sys
import zipfile

import yaml

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
VERSION_TAG = re.compile(r"\(v(\d+(?:\.\d+)*)\)\s*\Z")


def parse_frontmatter(text, label, errors):
    """Return the parsed frontmatter mapping, or None if it is unusable."""
    match = FRONTMATTER.match(text)
    if not match:
        errors.append(f"{label}: no YAML frontmatter block at the top of the file")
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        detail = str(exc).replace("\n", " ")
        errors.append(f"{label}: frontmatter is not valid YAML — {detail}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{label}: frontmatter is not a mapping")
        return None
    for key in ("name", "description"):
        if not data.get(key):
            errors.append(f"{label}: frontmatter is missing `{key}`")
            return None
    return data


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    errors = []

    sources = {}
    known_skills = set()
    source_paths = sorted(glob.glob("plugins/*/skills/*/SKILL.md"))
    if not source_paths:
        errors.append("no plugins/*/skills/*/SKILL.md found — wrong directory?")

    for path in source_paths:
        skill = os.path.basename(os.path.dirname(path))
        known_skills.add(skill)
        raw = open(path, "rb").read()
        data = parse_frontmatter(raw.decode("utf-8"), path, errors)
        if data is None:
            continue
        if data["name"] != skill:
            errors.append(f"{path}: name `{data['name']}` != directory `{skill}`")
        sources[skill] = (raw, data, path)

    for archive in sorted(glob.glob("dist/*.skill")):
        with zipfile.ZipFile(archive) as zf:
            packed = [n for n in zf.namelist() if n.endswith("/SKILL.md")]
            if len(packed) != 1:
                errors.append(f"{archive}: expected exactly 1 SKILL.md, found {len(packed)}")
                continue
            name = packed[0]
            skill = name.split("/")[0]
            raw = zf.read(name)

        if parse_frontmatter(raw.decode("utf-8"), f"{archive}::{name}", errors) is None:
            continue

        if skill not in sources:
            if skill not in known_skills:
                errors.append(f"{archive}: bundles `{skill}`, which has no source under plugins/")
            continue  # source already reported above; don't pile on cascading errors

        source_raw, source_data, source_path = sources[skill]
        if raw != source_raw:
            errors.append(
                f"{archive}: bundled SKILL.md differs from {source_path} "
                "— rebuild the .skill after editing the source"
            )

        tag = VERSION_TAG.search(source_data["description"])
        if not tag:
            errors.append(f"{source_path}: description has no trailing (vX.Y.Z) version tag")
        elif f"_v{tag.group(1)}.skill" not in os.path.basename(archive):
            errors.append(
                f"{archive}: filename version does not match the "
                f"(v{tag.group(1)}) tag in {source_path}"
            )

    if errors:
        print("Skill validation FAILED:\n")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"Skill validation passed: {len(sources)} skills, {len(glob.glob('dist/*.skill'))} bundles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
