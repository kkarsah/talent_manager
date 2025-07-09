#!/usr/bin/env python3
"""
Script to find and fix all references to alex_codemaster
"""

import os
import re
from pathlib import Path


def find_alex_references():
    """Find all files that reference alex_codemaster"""
    print("🔍 Searching for alex_codemaster references...")

    project_root = Path(".")
    problematic_files = []

    # Search all Python files
    for py_file in project_root.rglob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            if "alex_codemaster" in content:
                problematic_files.append(py_file)
                print(f"📄 Found reference in: {py_file}")

                # Show the problematic lines
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if "alex_codemaster" in line:
                        print(f"  Line {i}: {line.strip()}")

        except Exception as e:
            print(f"⚠️  Could not read {py_file}: {e}")

    return problematic_files


def fix_alex_references(files_to_fix):
    """Fix all alex_codemaster references"""
    print(f"\n🔧 Fixing {len(files_to_fix)} files...")

    for file_path in files_to_fix:
        print(f"📝 Fixing {file_path}...")

        # Backup the file
        backup_path = file_path.with_suffix(".py.backup")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Create backup
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  📁 Backup created: {backup_path}")

            # Fix the references
            original_content = content

            # Replace various forms of alex_codemaster references
            replacements = [
                ("alex_codemaster", "alex_codemaster"),
                (
                    "from talents.tech_educator.alex_codemaster",
                    "from talents.tech_educator.alex_codemaster",
                ),
                (
                    "talents.tech_educator.alex_codemaster",
                    "talents.tech_educator.alex_codemaster",
                ),
                ("import alex_codemaster", "import alex_codemaster"),
            ]

            for old, new in replacements:
                content = content.replace(old, new)

            # Write the fixed content
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  ✅ Fixed references in {file_path}")
            else:
                print(f"  ℹ️  No changes needed in {file_path}")

        except Exception as e:
            print(f"  ❌ Error fixing {file_path}: {e}")


def check_for_duplicate_files():
    """Check for any remaining alex_codemaster duplicate files"""
    print(f"\n🗃️  Checking for duplicate alex_codemaster files...")

    project_root = Path(".")
    alex_files = list(project_root.rglob("*alex_codemaster*.py"))

    print(f"Found {len(alex_files)} alex_codemaster files:")
    for file_path in alex_files:
        print(f"  📄 {file_path}")

    # Look for numbered versions
    numbered_files = [
        f for f in alex_files if re.search(r"alex_codemaster_\d+\.py$", str(f))
    ]

    if numbered_files:
        print(f"\n⚠️  Found {len(numbered_files)} numbered duplicate files:")
        for file_path in numbered_files:
            print(f"  🗑️  Should delete: {file_path}")

        response = input("\nDelete these duplicate files? (y/N): ")
        if response.lower() == "y":
            for file_path in numbered_files:
                try:
                    file_path.unlink()
                    print(f"  ✅ Deleted: {file_path}")
                except Exception as e:
                    print(f"  ❌ Could not delete {file_path}: {e}")


def clear_python_cache():
    """Clear Python cache"""
    print(f"\n🧹 Clearing Python cache...")

    import shutil

    cache_dirs = list(Path(".").rglob("__pycache__"))
    for cache_dir in cache_dirs:
        if cache_dir.is_dir():
            try:
                shutil.rmtree(cache_dir)
                print(f"  🗑️  Removed {cache_dir}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {cache_dir}: {e}")


def test_imports():
    """Test if the imports work after fixing"""
    print(f"\n🧪 Testing imports after fix...")

    try:
        # Test the specific import that was failing
        import sys

        sys.path.insert(0, str(Path(".").resolve()))

        from talents.tech_educator.alex_codemaster import AlexCodeMasterProfile

        print("  ✅ AlexCodeMasterProfile import: SUCCESS")

        from talents.tech_educator.alex_codemaster import AlexCodeMaster

        print("  ✅ AlexCodeMaster import: SUCCESS")

        # Test instantiation
        profile = AlexCodeMasterProfile()
        alex = AlexCodeMaster()
        print("  ✅ Class instantiation: SUCCESS")

        return True

    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("🔧 Alex CodeMaster Import Fixer")
    print("=" * 50)

    # Step 1: Find problematic files
    problematic_files = find_alex_references()

    if not problematic_files:
        print("✅ No alex_codemaster references found!")
        test_imports()
        return

    # Step 2: Fix the references
    fix_alex_references(problematic_files)

    # Step 3: Check for duplicate files
    check_for_duplicate_files()

    # Step 4: Clear cache
    clear_python_cache()

    # Step 5: Test imports
    success = test_imports()

    print("\n" + "=" * 50)
    if success:
        print("🎉 All imports fixed successfully!")
        print("✅ You can now run: python cli.py test-pipeline")
    else:
        print("⚠️  Some issues remain - check the errors above")

    print("\n📋 Summary of changes:")
    print(f"  📄 Files processed: {len(problematic_files)}")
    print("  🔄 Replaced alex_codemaster → alex_codemaster")
    print("  🧹 Cleared Python cache")
    print("  📁 Created backups (.py.backup)")


if __name__ == "__main__":
    main()
