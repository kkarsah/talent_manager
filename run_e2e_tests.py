#!/usr/bin/env python3
"""
Quick runner script for the Talent Manager E2E tests
Usage: python run_e2e_tests.py [--quick] [--component=<component>]
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Import the test suite
try:
    from e2e_test_suite import TalentManagerE2ETest
except ImportError:
    print("❌ Could not import e2e_test_suite. Make sure the file exists.")
    sys.exit(1)


async def run_quick_tests():
    """Run a quick subset of tests for rapid feedback"""
    print("🏃‍♂️ Running Quick Test Suite")
    print("=" * 40)

    test_suite = TalentManagerE2ETest()

    quick_tests = [
        ("🔧 Infrastructure", test_suite.test_infrastructure),
        ("🎭 Talent Management", test_suite.test_talent_management),
        ("🔌 API Endpoints", test_suite.test_api_endpoints),
    ]

    results = {"passed": 0, "failed": 0, "total": len(quick_tests)}

    for test_name, test_func in quick_tests:
        print(f"\n{test_name}")
        print("-" * 30)

        try:
            result = await test_func()
            if result.get("passed", False):
                results["passed"] += 1
                print(f"✅ {test_name}: PASSED")
            else:
                results["failed"] += 1
                print(f"❌ {test_name}: FAILED")
                for issue in result.get("issues", []):
                    print(f"   Issue: {issue}")
        except Exception as e:
            results["failed"] += 1
            print(f"💥 {test_name}: CRASHED - {e}")

    print(f"\n📊 Quick Test Results: {results['passed']}/{results['total']} passed")
    test_suite.cleanup()
    return results


async def run_component_test(component: str):
    """Run tests for a specific component"""
    print(f"🎯 Running {component} Component Tests")
    print("=" * 40)

    test_suite = TalentManagerE2ETest()

    component_map = {
        "infrastructure": test_suite.test_infrastructure,
        "talent": test_suite.test_talent_management,
        "content": test_suite.test_content_generation,
        "video": test_suite.test_video_creation,
        "ai": test_suite.test_ai_services,
        "analytics": test_suite.test_analytics,
        "api": test_suite.test_api_endpoints,
        "pipeline": test_suite.test_complete_pipeline,
    }

    if component not in component_map:
        print(f"❌ Unknown component: {component}")
        print(f"Available components: {', '.join(component_map.keys())}")
        return

    try:
        result = await component_map[component]()
        if result.get("passed", False):
            print(f"✅ {component} tests: PASSED")
        else:
            print(f"❌ {component} tests: FAILED")
            for issue in result.get("issues", []):
                print(f"   Issue: {issue}")

        # Show detailed test results
        print(f"\nDetailed Results:")
        for test_name, test_result in result.get("tests", {}).items():
            status = "✅" if test_result else "❌"
            print(f"   {status} {test_name}")

    except Exception as e:
        print(f"💥 {component} tests crashed: {e}")
    finally:
        test_suite.cleanup()


def show_help():
    """Show help information"""
    print("🎯 Talent Manager E2E Test Runner")
    print("=" * 40)
    print("\nUsage:")
    print("  python run_e2e_tests.py                 # Run full test suite")
    print("  python run_e2e_tests.py --quick         # Run quick tests only")
    print("  python run_e2e_tests.py --component=X   # Run specific component tests")
    print("\nAvailable Components:")
    print("  infrastructure  - Test server, database, dependencies")
    print("  talent         - Test talent creation and management")
    print("  content        - Test content generation")
    print("  video          - Test video creation pipeline")
    print("  ai             - Test AI services integration")
    print("  analytics      - Test analytics and metrics")
    print("  api            - Test all API endpoints")
    print("  pipeline       - Test complete content pipeline")
    print("\nExamples:")
    print("  python run_e2e_tests.py --component=talent")
    print("  python run_e2e_tests.py --quick")


async def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(description="Talent Manager E2E Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument(
        "--component", type=str, help="Run tests for specific component"
    )
    parser.add_argument(
        "--help-components", action="store_true", help="Show available components"
    )

    args = parser.parse_args()

    if args.help_components:
        show_help()
        return

    if args.component:
        await run_component_test(args.component)
    elif args.quick:
        await run_quick_tests()
    else:
        # Run full test suite
        test_suite = TalentManagerE2ETest()
        try:
            await test_suite.run_complete_test_suite()
        finally:
            test_suite.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test runner crashed: {e}")
        sys.exit(1)
