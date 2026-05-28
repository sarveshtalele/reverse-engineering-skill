#!/usr/bin/env python3
"""
Build distributable ZIP packages for the Reverse Engineer Skill.

Usage:
    python build_packages.py [--version 3.0.0]

Creates (in ./dist/):
    reverse-engineer-claude-code-skill-v{version}.zip
    reverse-engineer-github-copilot-skill-v{version}.zip
    reverse-engineer-agent-sdk-skill-v{version}.zip

Each ZIP is fully self-contained — the recipient just unzips and follows INSTALL.md.
"""

import argparse
import os
import shutil
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT        = Path(__file__).parent.parent          # repo root
PKG_DIR     = Path(__file__).parent                 # skill-packages/
DIST_DIR    = PKG_DIR / "dist"

PACKAGES = [
    ("01-claude-code-skill",      "reverse-engineer-claude-code-skill"),
    ("02-github-copilot-skill",   "reverse-engineer-github-copilot-skill"),
    ("03-agent-sdk-skill",        "reverse-engineer-agent-sdk-skill"),
]

# Engine files to include in every package
ENGINE_FILES = [
    "reverse_engineer_skill.py",
    "engine/__init__.py",
    "engine/pipeline.py",
    "engine/loaders.py",
    "engine/parsers.py",
    "engine/analyzer.py",
    "engine/ai_analysis.py",
    "engine/output_manager.py",
    "engine/evaluator.py",
    "engine/generators/__init__.py",
    "engine/generators/sdd.py",
    "engine/generators/dashboard.py",
    "engine/generators/report.py",
]

# Extra root files
EXTRA_FILES = [
    "run.bat",
    "run.sh",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def copy_engine_into(dest: Path) -> None:
    """Copy the shared engine files from ROOT into dest."""
    for rel in ENGINE_FILES:
        src = ROOT / rel
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy2(src, dst)
        else:
            print(f"  [warn] Source not found, skipping: {src}")

    for rel in EXTRA_FILES:
        src = ROOT / rel
        if src.exists():
            shutil.copy2(src, dest / rel)

    # Create outputs placeholder
    (dest / "outputs" / ".gitkeep").parent.mkdir(parents=True, exist_ok=True)
    (dest / "outputs" / ".gitkeep").touch()

    print(f"  [ok] Engine copied ({len(ENGINE_FILES)} files)")


def zip_folder(src_dir: Path, zip_path: Path, arc_root: str) -> None:
    """Zip src_dir into zip_path. Files are stored under arc_root/ inside the archive."""
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in src_dir.rglob("*"):
            if file.is_file() and "__pycache__" not in str(file):
                rel = file.relative_to(src_dir)
                zf.write(file, Path(arc_root) / rel)
    size_kb = zip_path.stat().st_size // 1024
    print(f"  [ok] {zip_path.name}  ({size_kb} KB)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Build Reverse Engineer Skill packages")
    parser.add_argument("--version", default="3.0.0", help="Version string (default: 3.0.0)")
    args = parser.parse_args()
    version = args.version

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nBuilding Reverse Engineer Skill packages  v{version}\n{'='*55}")

    for pkg_folder, pkg_name in PACKAGES:
        print(f"\n[{pkg_folder}]")
        src = PKG_DIR / pkg_folder

        if not src.exists():
            print(f"  [skip] Folder not found: {src}")
            continue

        # Build a temp assembly directory
        tmp = DIST_DIR / f"_tmp_{pkg_folder}"
        if tmp.exists():
            shutil.rmtree(tmp)
        shutil.copytree(src, tmp)

        # Inject shared engine into the temp copy
        copy_engine_into(tmp)

        # Zip it — arc_root is the clean folder name the user sees after unzip
        arc_root = f"{pkg_name}-v{version}"
        zip_name = f"{pkg_name}-v{version}.zip"
        zip_path = DIST_DIR / zip_name
        if zip_path.exists():
            zip_path.unlink()
        zip_folder(tmp, zip_path, arc_root)

        # Clean up temp dir
        shutil.rmtree(tmp)

    print(f"\n{'='*55}")
    print(f"Done. ZIP files in: {DIST_DIR.resolve()}\n")


if __name__ == "__main__":
    main()
