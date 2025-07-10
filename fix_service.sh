#!/bin/bash
# Quick fix for YouTube service import issues

echo "🔧 Quick YouTube Service Fix"
echo "=============================="

# Check if we have the secure service file
if [ -f "platforms/youtube/secure_service.py" ]; then
    echo "✅ Found secure_service.py"
    
    # Backup current service.py
    if [ -f "platforms/youtube/service.py" ]; then
        cp platforms/youtube/service.py platforms/youtube/service.py.backup
        echo "📁 Backed up existing service.py"
    fi
    
    # Copy secure service to main service file
    cp platforms/youtube/secure_service.py platforms/youtube/service.py
    
    # Add backward compatibility alias
    echo "" >> platforms/youtube/service.py
    echo "# Backward compatibility alias" >> platforms/youtube/service.py  
    echo "YouTubeService = SecureYouTubeService" >> platforms/youtube/service.py
    echo "" >> platforms/youtube/service.py
    echo "# Legacy import support" >> platforms/youtube/service.py
    echo "__all__ = ['SecureYouTubeService', 'YouTubeService']" >> platforms/youtube/service.py
    
    echo "✅ Updated service.py with secure version and backward compatibility"
    
else
    echo "❌ secure_service.py not found"
    echo "💡 Run this instead:"
    echo "   1. Save the 'Secure YouTube Service Implementation' as platforms/youtube/secure_service.py"
    echo "   2. Run this script again"
    exit 1
fi

# Test the imports
echo ""
echo "🧪 Testing imports..."

python3 -c "
try:
    from platforms.youtube.service import YouTubeService
    print('✅ YouTubeService import successful')
    
    from platforms.youtube.service import SecureYouTubeService  
    print('✅ SecureYouTubeService import successful')
    
    if YouTubeService == SecureYouTubeService:
        print('✅ Backward compatibility working')
    else:
        print('⚠️ Classes are different')
        
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Fix completed successfully!"
    echo "💡 Now you can run: python cli.py youtube-status"
else
    echo ""
    echo "❌ Fix failed - check the error above"
    exit 1
fi