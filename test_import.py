#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
"""

import sys
import traceback
from pathlib import Path


def test_import(module_name, class_name=None):
    """Test importing a module and optionally a class from it"""
    try:
        if class_name:
            exec(f"from {module_name} import {class_name}")
            print(f"✅ Successfully imported {class_name} from {module_name}")
            return True
        else:
            exec(f"import {module_name}")
            print(f"✅ Successfully imported {module_name}")
            return True
    except ImportError as e:
        print(
            f"❌ Failed to import {class_name or module_name} from {module_name}: {e}"
        )
        return False
    except Exception as e:
        print(
            f"❌ Unexpected error importing {class_name or module_name} from {module_name}: {e}"
        )
        traceback.print_exc()
        return False


def main():
    print("🧪 Testing imports for talent-manager project...\n")

    success_count = 0
    total_count = 0

    # Test the specific import that's failing
    print("🎯 Testing the problematic import:")
    total_count += 1
    if test_import("talents.tech_educator.alex_codemaster", "AlexCodeMasterProfile"):
        success_count += 1

    print("\n📦 Testing other core imports:")

    # Test other imports that might be related
    imports_to_test = [
        ("talents.tech_educator.alex_codemaster", "AlexCodeMaster"),
        ("core.pipeline.content_pipeline", "ContentPipeline"),
        ("core.content.generator", "ContentGenerator"),
        ("platforms.youtube.service", "YouTubeService"),
        ("core.database.config", "SessionLocal"),
        ("core.database.models", "Talent"),
        ("core.database.models", "ContentItem"),
    ]

    for module, class_name in imports_to_test:
        total_count += 1
        if test_import(module, class_name):
            success_count += 1

    print(f"\n📊 Import Test Results: {success_count}/{total_count} successful")

    if success_count == total_count:
        print("🎉 All imports working correctly!")
        return True
    else:
        print("⚠️  Some imports failed - check the errors above")
        return False


if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    success = main()
    sys.exit(0 if success else 1)
