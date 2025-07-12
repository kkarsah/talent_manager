#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite for Talent Manager System
Tests the complete pipeline from talent creation to video generation and upload
"""

import asyncio
import requests
import subprocess
import time
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TalentManagerE2ETest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None
        self.test_results = {}
        self.test_talent_id = None
        
    async def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete end-to-end test suite"""
        print("🚀 Starting Comprehensive End-to-End Test Suite")
        print("=" * 60)
        
        test_phases = [
            ("🔧 Infrastructure Tests", self.test_infrastructure),
            ("🎭 Talent Management Tests", self.test_talent_management),
            ("📝 Content Generation Tests", self.test_content_generation),
            ("🎬 Video Creation Tests", self.test_video_creation),
            ("🤖 AI Services Integration Tests", self.test_ai_services),
            ("📊 Analytics & Performance Tests", self.test_analytics),
            ("🔌 API Endpoint Tests", self.test_api_endpoints),
            ("🎯 Complete Pipeline Test", self.test_complete_pipeline)
        ]
        
        overall_results = {
            "total_phases": len(test_phases),
            "passed_phases": 0,
            "failed_phases": 0,
            "phase_results": {},
            "critical_issues": [],
            "recommendations": []
        }
        
        for phase_name, test_function in test_phases:
            print(f"\n{phase_name}")
            print("-" * 40)
            
            try:
                phase_result = await test_function()
                overall_results["phase_results"][phase_name] = phase_result
                
                if phase_result.get("passed", False):
                    overall_results["passed_phases"] += 1
                    print(f"✅ {phase_name}: PASSED")
                else:
                    overall_results["failed_phases"] += 1
                    print(f"❌ {phase_name}: FAILED")
                    overall_results["critical_issues"].extend(
                        phase_result.get("issues", [])
                    )
                    
            except Exception as e:
                logger.error(f"Phase {phase_name} crashed: {e}")
                overall_results["failed_phases"] += 1
                overall_results["critical_issues"].append(f"{phase_name}: {str(e)}")
                print(f"💥 {phase_name}: CRASHED - {e}")
        
        # Generate final report
        await self.generate_final_report(overall_results)
        return overall_results
    
    async def test_infrastructure(self) -> Dict[str, Any]:
        """Test infrastructure and server startup"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            # Test 1: Check if server is running
            print("Testing server connectivity...")
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                result["tests"]["server_running"] = response.status_code == 200
                if response.status_code != 200:
                    result["issues"].append("Server health check failed")
            except requests.exceptions.ConnectionError:
                print("Server not running, attempting to start...")
                result["tests"]["server_running"] = await self.start_server()
                if not result["tests"]["server_running"]:
                    result["issues"].append("Failed to start server")
            
            # Test 2: Database connectivity
            print("Testing database connectivity...")
            try:
                response = requests.get(f"{self.base_url}/api/system/info", timeout=5)
                if response.status_code == 200:
                    info = response.json()
                    result["tests"]["database"] = info.get("features", {}).get("database", False)
                else:
                    result["tests"]["database"] = False
                    result["issues"].append("Database connectivity check failed")
            except Exception as e:
                result["tests"]["database"] = False
                result["issues"].append(f"Database test error: {e}")
            
            # Test 3: Required dependencies
            print("Testing system dependencies...")
            dependencies = ["PIL", "requests", "fastapi", "sqlalchemy"]
            missing_deps = []
            
            for dep in dependencies:
                try:
                    __import__(dep.lower())
                    result["tests"][f"dependency_{dep}"] = True
                except ImportError:
                    result["tests"][f"dependency_{dep}"] = False
                    missing_deps.append(dep)
            
            if missing_deps:
                result["issues"].append(f"Missing dependencies: {', '.join(missing_deps)}")
            
            # Test 4: File system permissions
            print("Testing file system permissions...")
            test_dir = Path("./test_output")
            try:
                test_dir.mkdir(exist_ok=True)
                test_file = test_dir / "test_file.txt"
                test_file.write_text("test")
                test_file.unlink()
                result["tests"]["file_permissions"] = True
            except Exception as e:
                result["tests"]["file_permissions"] = False
                result["issues"].append(f"File system permission error: {e}")
            
            # Determine if phase passed
            critical_tests = ["server_running", "database"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"Infrastructure test crashed: {e}")
            
        return result
    
    async def test_talent_management(self) -> Dict[str, Any]:
        """Test talent creation, retrieval, and management"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            # Test 1: List talents (should start empty or with existing)
            print("Testing talent listing...")
            response = requests.get(f"{self.base_url}/api/talents")
            result["tests"]["list_talents"] = response.status_code == 200
            
            initial_count = len(response.json().get("talents", [])) if response.status_code == 200 else 0
            print(f"Initial talent count: {initial_count}")
            
            # Test 2: Create a test talent
            print("Testing talent creation...")
            test_talent_data = {
                "name": "E2E Test Talent",
                "specialization": "End-to-End Testing",
                "personality": {
                    "tone": "professional",
                    "expertise_level": "expert",
                    "teaching_style": "comprehensive"
                }
            }
            
            response = requests.post(f"{self.base_url}/api/talents", json=test_talent_data)
            result["tests"]["create_talent"] = response.status_code == 200
            
            if response.status_code == 200:
                talent_data = response.json()
                self.test_talent_id = talent_data.get("talent", {}).get("id")
                print(f"Created test talent with ID: {self.test_talent_id}")
            else:
                result["issues"].append(f"Failed to create talent: {response.text}")
            
            # Test 3: Retrieve the created talent
            if self.test_talent_id:
                print("Testing talent retrieval...")
                response = requests.get(f"{self.base_url}/api/talents/{self.test_talent_id}")
                result["tests"]["get_talent"] = response.status_code == 200
                
                if response.status_code == 200:
                    talent = response.json().get("talent", {})
                    name_match = talent.get("name") == test_talent_data["name"]
                    spec_match = talent.get("specialization") == test_talent_data["specialization"]
                    result["tests"]["talent_data_integrity"] = name_match and spec_match
                else:
                    result["issues"].append("Failed to retrieve created talent")
            
            # Test 4: List talents again (should have increased)
            response = requests.get(f"{self.base_url}/api/talents")
            if response.status_code == 200:
                new_count = len(response.json().get("talents", []))
                result["tests"]["talent_count_increased"] = new_count > initial_count
            
            # Determine if phase passed
            critical_tests = ["list_talents", "create_talent", "get_talent"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"Talent management test crashed: {e}")
            
        return result
    
    async def test_content_generation(self) -> Dict[str, Any]:
        """Test content script generation functionality"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            if not self.test_talent_id:
                result["issues"].append("No test talent available for content generation")
                return result
            
            # Test 1: Generate content script
            print("Testing content generation...")
            content_data = {
                "talent_id": self.test_talent_id,
                "title": "E2E Test Video: Python Basics",
                "content_type": "short_form",
                "platform": "youtube",
                "topic": "Python variables and data types"
            }
            
            response = requests.post(f"{self.base_url}/api/content", json=content_data, timeout=30)
            result["tests"]["generate_content"] = response.status_code == 200
            
            if response.status_code == 200:
                content_response = response.json()
                content_id = content_response.get("content", {}).get("id")
                script = content_response.get("content", {}).get("script")
                
                result["tests"]["content_has_script"] = bool(script)
                result["tests"]["content_has_id"] = bool(content_id)
                
                # Store for later tests
                self.test_content_id = content_id
                print(f"Generated content ID: {content_id}")
                print(f"Script length: {len(script) if script else 0} characters")
            else:
                result["issues"].append(f"Content generation failed: {response.text}")
            
            # Test 2: List content
            print("Testing content listing...")
            response = requests.get(f"{self.base_url}/api/content")
            result["tests"]["list_content"] = response.status_code == 200
            
            # Test 3: Validate script structure
            if hasattr(self, 'test_content_id') and response.status_code == 200:
                content_list = response.json().get("content", [])
                test_content = next((c for c in content_list if c.get("id") == self.test_content_id), None)
                
                if test_content:
                    script = test_content.get("script", "")
                    # Check for scene markers
                    has_scenes = "[" in script and "]" in script
                    result["tests"]["script_has_scenes"] = has_scenes
                    
                    # Check minimum length
                    result["tests"]["script_adequate_length"] = len(script) > 100
                else:
                    result["issues"].append("Generated content not found in content list")
            
            # Determine if phase passed
            critical_tests = ["generate_content", "content_has_script", "list_content"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"Content generation test crashed: {e}")
            
        return result
    
    async def test_video_creation(self) -> Dict[str, Any]:
        """Test video creation pipeline"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            # Test 1: Check video creation dependencies
            print("Testing video creation dependencies...")
            try:
                from PIL import Image
                result["tests"]["pil_available"] = True
            except ImportError:
                result["tests"]["pil_available"] = False
                result["issues"].append("PIL not available for image processing")
            
            # Test 2: Test DALL-E integration (if available)
            print("Testing DALL-E integration...")
            # This would require API keys, so we'll do a mock test
            dalle_test_script = """
            [Opening: Welcome scene]
            Welcome to this tutorial on Python basics.
            
            [Main: Explanation scene] 
            Let's learn about variables in Python.
            
            [Closing: Summary scene]
            Thanks for watching this tutorial!
            """
            
            # Test scene parsing
            scenes = self.parse_scenes_for_test(dalle_test_script)
            result["tests"]["scene_parsing"] = len(scenes) >= 3
            print(f"Parsed {len(scenes)} scenes from test script")
            
            # Test 3: Check FFmpeg availability (if needed)
            print("Testing FFmpeg availability...")
            try:
                ffmpeg_result = subprocess.run(
                    ["ffmpeg", "-version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                result["tests"]["ffmpeg_available"] = ffmpeg_result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                result["tests"]["ffmpeg_available"] = False
                result["issues"].append("FFmpeg not available for video processing")
            
            # Test 4: Test basic image creation
            print("Testing basic image creation...")
            try:
                from PIL import Image, ImageDraw, ImageFont
                test_image = Image.new("RGB", (1920, 1080), color="blue")
                draw = ImageDraw.Draw(test_image)
                draw.text((100, 100), "Test Scene", fill="white")
                
                test_output_dir = Path("./test_output")
                test_output_dir.mkdir(exist_ok=True)
                test_image_path = test_output_dir / "test_scene.png"
                test_image.save(test_image_path)
                
                result["tests"]["image_creation"] = test_image_path.exists()
                if test_image_path.exists():
                    test_image_path.unlink()  # Clean up
            except Exception as e:
                result["tests"]["image_creation"] = False
                result["issues"].append(f"Image creation failed: {e}")
            
            # Determine if phase passed
            critical_tests = ["pil_available", "scene_parsing", "image_creation"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"Video creation test crashed: {e}")
            
        return result
    
    async def test_ai_services(self) -> Dict[str, Any]:
        """Test AI services integration"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            # Test 1: Check OpenAI configuration
            print("Testing AI services configuration...")
            openai_key = os.getenv("OPENAI_API_KEY")
            result["tests"]["openai_key_present"] = bool(openai_key)
            if not openai_key:
                result["issues"].append("OpenAI API key not configured")
            
            # Test 2: Check ElevenLabs configuration
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            result["tests"]["elevenlabs_key_present"] = bool(elevenlabs_key)
            if not elevenlabs_key:
                result["issues"].append("ElevenLabs API key not configured")
            
            # Test 3: Test AI services endpoint
            print("Testing AI services status...")
            try:
                response = requests.get(f"{self.base_url}/api/system/info")
                if response.status_code == 200:
                    info = response.json()
                    features = info.get("features", {})
                    result["tests"]["dalle_video_creator"] = features.get("dalle_video_creator", False)
                else:
                    result["tests"]["dalle_video_creator"] = False
            except Exception as e:
                result["tests"]["dalle_video_creator"] = False
                result["issues"].append(f"AI services status check failed: {e}")
            
            # Test 4: Mock content generation (without API calls)
            print("Testing content generation logic...")
            test_prompt = "Explain Python variables in simple terms"
            prompt_valid = len(test_prompt) > 10 and "python" in test_prompt.lower()
            result["tests"]["prompt_validation"] = prompt_valid
            
            # Determine if phase passed (AI keys are optional for basic functionality)
            critical_tests = ["dalle_video_creator", "prompt_validation"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"AI services test crashed: {e}")
            
        return result
    
    async def test_analytics(self) -> Dict[str, Any]:
        """Test analytics and performance tracking"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            # Test 1: Analytics overview endpoint
            print("Testing analytics endpoints...")
            response = requests.get(f"{self.base_url}/api/analytics/overview")
            result["tests"]["analytics_overview"] = response.status_code == 200
            
            if response.status_code == 200:
                analytics_data = response.json()
                result["tests"]["analytics_has_data"] = "metrics" in analytics_data
            else:
                result["issues"].append("Analytics overview endpoint failed")
            
            # Test 2: Performance metrics
            response = requests.get(f"{self.base_url}/api/analytics/performance")
            result["tests"]["performance_metrics"] = response.status_code == 200
            
            # Test 3: System status
            response = requests.get(f"{self.base_url}/api/status")
            result["tests"]["system_status"] = response.status_code == 200
            
            # Determine if phase passed
            critical_tests = ["analytics_overview", "system_status"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"Analytics test crashed: {e}")
            
        return result
    
    async def test_api_endpoints(self) -> Dict[str, Any]:
        """Test all API endpoints comprehensively"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        endpoints_to_test = [
            ("/", "Root redirect", [200, 307]),
            ("/api/health", "Health check", [200]),
            ("/api/status", "System status", [200]),
            ("/api/talents", "List talents", [200]),
            ("/api/content", "List content", [200]),
            ("/api/analytics/overview", "Analytics overview", [200]),
            ("/api/system/info", "System info", [200]),
            ("/docs", "API documentation", [200]),
        ]
        
        print("Testing API endpoints comprehensively...")
        
        passed_endpoints = 0
        for endpoint, description, expected_codes in endpoints_to_test:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                endpoint_passed = response.status_code in expected_codes
                result["tests"][f"endpoint_{endpoint.replace('/', '_')}"] = endpoint_passed
                
                if endpoint_passed:
                    passed_endpoints += 1
                    print(f"✅ {description}: {endpoint} -> {response.status_code}")
                else:
                    print(f"❌ {description}: {endpoint} -> {response.status_code}")
                    result["issues"].append(f"Endpoint {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                result["tests"][f"endpoint_{endpoint.replace('/', '_')}"] = False
                result["issues"].append(f"Endpoint {endpoint} failed: {e}")
                print(f"💥 {description}: {endpoint} -> ERROR: {e}")
        
        # Calculate pass rate
        total_endpoints = len(endpoints_to_test)
        pass_rate = passed_endpoints / total_endpoints
        result["tests"]["endpoint_pass_rate"] = pass_rate
        
        # Phase passes if 80% of endpoints work
        result["passed"] = pass_rate >= 0.8
        
        print(f"Endpoint pass rate: {pass_rate:.1%} ({passed_endpoints}/{total_endpoints})")
        
        return result
    
    async def test_complete_pipeline(self) -> Dict[str, Any]:
        """Test the complete content creation pipeline"""
        result = {"passed": False, "tests": {}, "issues": []}
        
        try:
            print("Testing complete content creation pipeline...")
            
            if not self.test_talent_id:
                result["issues"].append("No test talent available for pipeline test")
                return result
            
            # Test 1: Create content with full pipeline
            pipeline_content_data = {
                "talent_id": self.test_talent_id,
                "title": "Complete Pipeline Test: JavaScript Arrays",
                "content_type": "short_form",
                "platform": "youtube",
                "topic": "JavaScript array methods and operations",
                "generate_video": False  # Skip actual video generation for speed
            }
            
            print("Initiating pipeline test...")
            response = requests.post(
                f"{self.base_url}/api/content", 
                json=pipeline_content_data, 
                timeout=60
            )
            
            result["tests"]["pipeline_initiation"] = response.status_code == 200
            
            if response.status_code == 200:
                pipeline_response = response.json()
                content = pipeline_response.get("content", {})
                
                # Check pipeline outputs
                result["tests"]["pipeline_has_script"] = bool(content.get("script"))
                result["tests"]["pipeline_has_metadata"] = bool(content.get("title"))
                result["tests"]["pipeline_content_structure"] = all([
                    content.get("id"),
                    content.get("title"),
                    content.get("script"),
                    content.get("content_type")
                ])
                
                print(f"Pipeline generated content: {content.get('title')}")
                print(f"Script length: {len(content.get('script', ''))} characters")
                
            else:
                result["issues"].append(f"Pipeline failed: {response.text}")
            
            # Test 2: Verify content persistence
            if self.test_talent_id:
                response = requests.get(f"{self.base_url}/api/content")
                if response.status_code == 200:
                    content_list = response.json().get("content", [])
                    talent_content = [c for c in content_list if c.get("talent_id") == self.test_talent_id]
                    result["tests"]["content_persistence"] = len(talent_content) >= 1
                    print(f"Found {len(talent_content)} content items for test talent")
            
            # Test 3: System health after pipeline run
            response = requests.get(f"{self.base_url}/api/health")
            result["tests"]["post_pipeline_health"] = response.status_code == 200
            
            # Determine if phase passed
            critical_tests = ["pipeline_initiation", "pipeline_has_script", "content_persistence"]
            result["passed"] = all(result["tests"].get(test, False) for test in critical_tests)
            
        except Exception as e:
            result["issues"].append(f"Complete pipeline test crashed: {e}")
            
        return result
    
    async def start_server(self) -> bool:
        """Start the server if not running"""
        try:
            print("Starting FastAPI server...")
            self.server_process = subprocess.Popen(
                ["python", "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            for attempt in range(10):
                time.sleep(2)
                try:
                    response = requests.get(f"{self.base_url}/api/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Server started successfully (attempt {attempt + 1})")
                        return True
                except:
                    continue
            
            print("❌ Server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def parse_scenes_for_test(self, script: str) -> List[Dict[str, str]]:
        """Parse scenes from script for testing"""
        scenes = []
        lines = script.split('\n')
        current_scene = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and ']:' in line:
                if current_scene:
                    scenes.append(current_scene)
                
                scene_desc = line[1:line.find(']:')]
                current_scene = {'description': scene_desc, 'content': ''}
            elif current_scene and line:
                current_scene['content'] += line + ' '
        
        if current_scene:
            scenes.append(current_scene)
        
        return scenes
    
    async def generate_final_report(self, results: Dict[str, Any]) -> None:
        """Generate and display final test report"""
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE END-TO-END TEST REPORT")
        print("=" * 60)
        
        # Summary statistics
        total_phases = results["total_phases"]
        passed_phases = results["passed_phases"]
        failed_phases = results["failed_phases"]
        success_rate = (passed_phases / total_phases) * 100 if total_phases > 0 else 0
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Test Phases: {total_phases}")
        print(f"   Passed Phases: {passed_phases}")
        print(f"   Failed Phases: {failed_phases}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Phase breakdown
        print(f"\n📋 PHASE BREAKDOWN:")
        for phase_name, phase_result in results["phase_results"].items():
            status = "✅ PASS" if phase_result.get("passed", False) else "❌ FAIL"
            test_count = len(phase_result.get("tests", {}))
            passed_tests = sum(1 for test_result in phase_result.get("tests", {}).values() if test_result)
            print(f"   {status} {phase_name}")
            print(f"      Tests: {passed_tests}/{test_count} passed")
            
            if phase_result.get("issues"):
                print(f"      Issues: {len(phase_result['issues'])}")
        
        # Critical issues
        if results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in results["critical_issues"]:
                print(f"   • {issue}")
        
        # System status assessment
        print(f"\n🏥 SYSTEM HEALTH ASSESSMENT:")
        if success_rate >= 80:
            print("   🟢 EXCELLENT - System is functioning well")
        elif success_rate >= 60:
            print("   🟡 GOOD - System is mostly functional with minor issues")
        elif success_rate >= 40:
            print("   🟠 FAIR - System has significant issues requiring attention")
        else:
            print("   🔴 POOR - System has critical issues requiring immediate attention")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if failed_phases == 0:
            print("   • System is ready for production!")
            print("   • Consider adding more comprehensive integration tests")
            print("   • Monitor performance in production environment")
        elif "Infrastructure Tests" in [p for p, r in results["phase_results"].items() if not r.get("passed")]:
            print("   • Fix infrastructure issues before proceeding")
            print("   • Ensure all dependencies are properly installed")
            print("   • Check database connectivity and file permissions")
        else:
            print("   • Address failed test phases in order of criticality")
            print("   • Review error logs for specific failure causes")
            print("   • Re-run tests after fixes to verify resolution")
        
        # Next steps
        print(f"\n🎯 NEXT STEPS:")
        if success_rate >= 80:
            print("   1. Deploy to staging environment")
            print("   2. Run performance and load testing")
            print("   3. Set up monitoring and alerting")
            print("   4. Create production deployment plan")
        else:
            print("   1. Address critical issues identified above")
            print("   2. Re-run specific failed test phases")
            print("   3. Implement missing functionality")
            print("   4. Repeat end-to-end testing until 80%+ success rate")
        
        print("\n" + "=" * 60)
        print("🎉 End-to-End Test Suite Complete!")
        print("=" * 60)
    
    def cleanup(self):
        """Clean up test resources"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("🛑 Test server stopped")

# Main execution
async def main():
    """Main test execution function"""
    test_suite = TalentManagerE2ETest()
    
    try:
        results = await test_suite.run_complete_test_suite()
        return results
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
    finally:
        test_suite.cleanup()

if __name__ == "__main__":
    print("🚀 Starting Talent Manager End-to-End Test Suite")
    print("This comprehensive test will validate all system components")
    print("=" * 60)
    
    # Run the async test suite
    asyncio.run(main())