import re


def integrate_services():
    """Automatically integrate services into the existing pipeline"""

    # Read the current pipeline file
    with open("core/pipeline/enhanced_content_pipeline.py", "r") as f:
        content = f.read()

    # Add imports at the top (after existing imports)
    import_lines = """from core.content.enhanced_scene_service import EnhancedSceneService
from core.content.video_stitching_service import VideoStitchingService
from typing import List, Dict  # Add if not already imported
import uuid  # Add if not already imported"""

    # Find where to insert imports (after the last import statement)
    import_pattern = r"(from .* import .*|import .*)\n"
    imports = re.findall(import_pattern, content)
    if imports:
        last_import = imports[-1]
        content = content.replace(
            last_import + "\n", last_import + "\n" + import_lines + "\n\n"
        )

    # Add service properties after the existing properties
    service_properties = """
    @property
    def scene_service(self):
        \"\"\"Enhanced scene generation service\"\"\"
        if not hasattr(self, '_scene_service') or self._scene_service is None:
            self._scene_service = EnhancedSceneService()
        return self._scene_service

    @property  
    def stitching_service(self):
        \"\"\"Video stitching service\"\"\"
        if not hasattr(self, '_stitching_service') or self._stitching_service is None:
            self._stitching_service = VideoStitchingService()
        return self._stitching_service
"""

    # Find where to insert properties (after video_creator property)
    video_creator_pattern = (
        r"(@property\s+def video_creator\(self\):.*?return self\._video_creator)"
    )
    match = re.search(video_creator_pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(1), match.group(1) + service_properties)

    # Write the updated content
    with open("core/pipeline/enhanced_content_pipeline.py", "w") as f:
        f.write(content)

    print("✅ Services integrated into pipeline!")


if __name__ == "__main__":
    integrate_services()
