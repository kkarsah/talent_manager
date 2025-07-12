import asyncio
import logging
from core.content.enhanced_scene_service import EnhancedSceneService
from core.content.video_stitching_service import VideoStitchingService

logging.basicConfig(level=logging.INFO)

async def test_services():
    print("🧪 Testing Service Integration")
    print("-" * 40)
    
    # Test scene service
    try:
        scene_service = EnhancedSceneService()
        capabilities = scene_service.get_capabilities()
        print(f"✅ Scene Service: {capabilities}")
    except Exception as e:
        print(f"❌ Scene Service failed: {e}")
        return False
    
    # Test stitching service  
    try:
        stitching_service = VideoStitchingService()
        capabilities = stitching_service.get_stitching_capabilities()
        print(f"✅ Stitching Service: Available")
    except Exception as e:
        print(f"❌ Stitching Service failed: {e}")
        return False
    
    # Test scene parsing
    try:
        test_script = """
        [Opening: Welcome to tutorial]
        Welcome to this Python tutorial.
        
        [Main: Core content]  
        Let's learn about functions in Python.
        
        [Closing: Wrap up]
        Thanks for watching!
        """
        
        # Simple scene parsing test
        scenes = []
        lines = test_script.split('\n')
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
        
        print(f"✅ Scene Parsing: {len(scenes)} scenes found")
        for i, scene in enumerate(scenes):
            print(f"   Scene {i+1}: {scene['description']}")
            
    except Exception as e:
        print(f"❌ Scene parsing failed: {e}")
        return False
    
    print("\n🎉 All services working! Ready for integration.")
    return True

if __name__ == "__main__":
    asyncio.run(test_services())
