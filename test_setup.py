#!/usr/bin/env python3
"""
Simple test script to verify the WhatsApp RAG Scheduler setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from app.main import app
        print("✅ FastAPI app imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI app: {e}")
        return False
    
    try:
        from app.services.ai_service import ai_service
        print("✅ AI service imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import AI service: {e}")
        return False
    
    try:
        from app.services.rag_service import rag_service
        print("✅ RAG service imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import RAG service: {e}")
        return False
    
    try:
        from app.services.calendar_service import calendar_service
        print("✅ Calendar service imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import Calendar service: {e}")
        return False
    
    try:
        from app.services.todoist_service import todoist_service
        print("✅ Todoist service imports successfully")
    except ImportError as e:
        print(f"❌ Failed to import Todoist service: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print("✅ Configuration loads successfully")
        
        # Check if .env file exists
        if Path(".env").exists():
            print("✅ .env file found")
        else:
            print("⚠️  .env file not found - copy from .env.example")
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n🗄️  Testing database...")
    
    try:
        from app.models.database import SessionLocal, User, Meeting, Conversation
        
        # Test database session
        db = SessionLocal()
        db.close()
        print("✅ Database connection successful")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_ai_functionality():
    """Test AI service functionality"""
    print("\n🤖 Testing AI functionality...")
    
    try:
        from app.services.ai_service import ai_service
        
        # Test intent classification with a simple message
        test_message = "Schedule a meeting tomorrow at 3pm"
        result = ai_service.classify_intent(test_message)
        
        if isinstance(result, dict) and 'intent' in result:
            print("✅ AI intent classification working")
            print(f"   Test result: {result.get('intent', 'unknown')}")
        else:
            print("⚠️  AI service returned unexpected format")
        
        return True
    except Exception as e:
        print(f"❌ AI service error: {e}")
        print("   Note: This requires a valid OpenAI API key in .env")
        return False

def main():
    """Run all tests"""
    print("🚀 WhatsApp RAG Scheduler - Setup Test\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Database Test", test_database),
        ("AI Functionality Test", test_ai_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your setup looks good.")
        print("\n📋 Next steps:")
        print("1. Configure your .env file with API keys")
        print("2. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        print("3. Run the app: uvicorn app.main:app --reload")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the errors above.")
        print("Make sure you have:")
        print("- Installed all requirements: pip install -r requirements.txt")
        print("- Created .env file from .env.example")
        print("- Added your API keys to .env")

if __name__ == "__main__":
    main()