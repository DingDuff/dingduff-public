#!/usr/bin/env python3
"""Repackage every skill under plugins/ into its dist/*.skill bundle.

A `.skill` file is a zip of the skill directory, rooted at the skill's own name,
named `dingduff_<skill>_v<version>.skill` where `<version>` is the `(vX.Y.Z)` tag
at the end of the SKILL.md description. Editing a source file and forgetting to
rebuild ships a stale bundle to everyone who downloads by hand; this script plus
`validate_skills.py` (which compares the bundled SKILL.md to the source byte for
byte) closes that gap.

`tests/` is source-only and is left out of the bundle — it exists to check the
scripts in CI, not to run on an attorney's machine. Everything else in the skill
directory ships, including LICENSE.md.

Run from anywhere: python3 scripts/build_dist.py
Add --check to verify the existing bundles are current without writing anything.
"""

import argparse
import glob
import os
import re
import sys
import zipfile

VERSION_TAG = re.compile(r"\(v(\d+(?:\.\d+)*)\)\s*\Z")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
DESCRIPTION = re.compile(r"^description:\s*(.*?)(?=^\w[\w-]*:|\Z)", re.M | re.S)

# Directories that exist for development and never ship inside a .skill.
EXCLUDED_DIRS = {"tests", "dev", "__pycache__"}
EXCLUDED_NAMES = {".DS_Store"}


def skill_version(skill_md_path):
    """Pull the (vX.Y.Z) tag off the end of the SKILL.md description."""
    raw = open(skill_md_path, encoding="utf-8").read()
    front = FRONTMATTER.match(raw)
    if not front:
        raise SystemExit(f"{skill_md_path}: no YAML frontmatter block")
    field = DESCRIPTION.search(front.group(1))
    if not field:
        raise SystemExit(f"{skill_md_path}: frontmatter has no `description`")
    tag = VERSION_TAG.search(field.group(1).strip().rstrip('"').rstrip("'"))
    if not tag:
        raise SystemExit(f"{skill_md_path}: description has no trailing (vX.Y.Z) tag")
    return tag.group(1)


def bundle_members(skill_dir):
    """Every path that ships, as (absolute path, name inside the archive) pairs."""
    skill = os.path.basename(skill_dir)
    members = []
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        for filename in sorted(filenames):
            if filename in EXCLUDED_NAMES:
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, skill_dir)
            members.append((full, f"{skill}/{rel}"))
    return members


def write_bundle(skill_dir, archive):
    # Fixed timestamps and permissions so rebuilding an unchanged skill produces
    # a byte-identical file — otherwise every build shows up as a diff in git.
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for full, name in bundle_members(skill_dir):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, open(full, "rb").read())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if any bundle is missing or out of date; write nothing",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    os.makedirs("dist", exist_ok=True)

    expected = set()
    stale = []

    for skill_md in sorted(glob.glob("plugins/*/skills/*/SKILL.md")):
        skill_dir = os.path.dirname(skill_md)
        skill = os.path.basename(skill_dir)
        version = skill_version(skill_md)
        # dist filenames drop the `dingduff-` prefix: dingduff_legal-research_v2.4.skill
        short = skill[len("dingduff-"):] if skill.startswith("dingduff-") else skill
        archive = os.path.join("dist", f"dingduff_{short}_v{version}.skill")
        expected.add(archive)

        before = open(archive, "rb").read() if os.path.exists(archive) else None
        if args.check:
            if before is None:
                stale.append(f"{archive}: missing")
                continue
            write_bundle(skill_dir, archive + ".tmp")
            after = open(archive + ".tmp", "rb").read()
            os.remove(archive + ".tmp")
            if after != before:
                stale.append(f"{archive}: out of date — rerun scripts/build_dist.py")
            continue

        write_bundle(skill_dir, archive)
        state = "unchanged" if before == open(archive, "rb").read() else "built"
        print(f"  {state:9s} {archive}")

    orphans = sorted(set(glob.glob("dist/*.skill")) - expected)
    for orphan in orphans:
        stale.append(f"{orphan}: no skill builds this — an old version left behind?")

    if stale:
        print("Bundle check FAILED:\n")
        for line in stale:
            print(f"  - {line}")
        return 1

    print(f"{len(expected)} bundles {'checked' if args.check else 'written'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
