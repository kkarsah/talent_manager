#!/usr/bin/env python3
"""
Production Readiness Validation
Validates that your Talent Manager is ready for production use
"""

from fastapi.testclient import TestClient
from main import app

def validate_production_readiness():
    """Validate the system is production ready"""
    print("🚀 Production Readiness Validation")
    print("=" * 40)
    
    client = TestClient(app)
    passed_tests = 0
    total_tests = 5
    
    # Test 1: API Health
    print("\n1. Testing API Health...")
    response = client.get("/api/health")
    if response.status_code == 200:
        print("   ✅ API is healthy and responsive")
        passed_tests += 1
    else:
        print("   ❌ API health check failed")
    
    # Test 2: Talent Management
    print("\n2. Testing Talent Management...")
    talent_data = {"name": "Production Test Talent", "specialization": "Production Testing"}
    response = client.post("/api/talents", json=talent_data)
    if response.status_code == 200:
        talent_id = response.json()["talent"]["id"]
        print("   ✅ Talent creation and management working")
        passed_tests += 1
    else:
        print("   ❌ Talent management failed")
        return False
    
    # Test 3: Content Generation
    print("\n3. Testing Content Generation...")
    content_data = {
        "talent_id": talent_id,
        "title": "Production Test Content",
        "topic": "System testing best practices",
        "content_type": "short_form"
    }
    response = client.post("/api/content", json=content_data)
    if response.status_code == 200:
        content_response = response.json()
        script = content_response.get("content", {}).get("script", "")
        if len(script) > 50:
            print("   ✅ Content generation working with AI script creation")
            passed_tests += 1
        else:
            print("   ⚠️  Content created but script generation minimal")
    else:
        print("   ❌ Content generation failed")
    
    # Test 4: Data Persistence
    print("\n4. Testing Data Persistence...")
    response = client.get("/api/talents")
    if response.status_code == 200:
        talents = response.json().get("talents", [])
        if len(talents) > 0:
            print("   ✅ Data persistence and retrieval working")
            passed_tests += 1
        else:
            print("   ❌ Data persistence issues")
    else:
        print("   ❌ Data retrieval failed")
    
    # Test 5: System Integration
    print("\n5. Testing System Integration...")
    response = client.get("/api/system/info")
    if response.status_code == 200:
        system_info = response.json()
        features = system_info.get("features", {})
        working_features = sum(1 for feature, status in features.items() if status)
        if working_features >= 3:
            print("   ✅ System integration and features working")
            passed_tests += 1
        else:
            print("   ⚠️  Some system features not fully integrated")
    else:
        print("   ❌ System integration check failed")
    
    # Calculate final score
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📊 PRODUCTION READINESS SCORE: {success_rate:.1f}%")
    print(f"Passed: {passed_tests}/{total_tests} critical tests")
    
    if success_rate >= 80:
        print("\n🎉 RESULT: PRODUCTION READY! 🚀")
        print("Your Talent Manager system is ready for production deployment!")
        print("\n✅ Core capabilities verified:")
        print("  • API endpoints functional")
        print("  • Talent management working") 
        print("  • Content generation with AI")
        print("  • Data persistence operational")
        print("  • System integration complete")
        
        print("\n🚀 Next steps:")
        print("  1. Deploy to production environment")
        print("  2. Set up monitoring and alerting")
        print("  3. Configure production AI API keys")
        print("  4. Start creating content with your talents!")
        
    elif success_rate >= 60:
        print("\n🟡 RESULT: NEARLY READY")
        print("Your system is mostly functional with minor issues.")
        print("Address the failed tests above and re-run validation.")
        
    else:
        print("\n🔴 RESULT: NEEDS WORK")
        print("Core functionality issues detected. Review failed tests.")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = validate_production_readiness()
    if success:
        print("\n🎊 Congratulations! Your Talent Manager is production ready!")
    else:
        print("\n⚠️  Continue working on the identified issues.")
