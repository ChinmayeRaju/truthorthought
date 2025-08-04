#!/usr/bin/env python3
"""
Startup script for the Truth or Thought Web UI
Multi-Role Prompting System for Fact vs Opinion Analysis
"""

import os
import sys
from app import app

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with your Google API key:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return False
    
    return True

def main():
    print("=" * 60)
    print("Truth or Thought - Web UI")
    print("Multi-Role Prompting System for Fact vs Opinion Analysis")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print(" Environment check passed")
    print(" Starting web server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n Server stopped by user")
    except Exception as e:
        print(f"\n Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()