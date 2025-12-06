import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

print("-" * 20)
print("Checking for rss_service.py...")
if os.path.exists("rss_service.py"):
    print("✅ rss_service.py exists")
else:
    print("❌ rss_service.py NOT found")

print("-" * 20)
print("Attempting to import feedparser...")
try:
    import feedparser
    print(f"✅ feedparser imported: {feedparser.__file__}")
except ImportError as e:
    print(f"❌ Failed to import feedparser: {e}")

print("-" * 20)
print("Attempting to import rss_service...")
try:
    import rss_service
    print(f"✅ rss_service imported: {rss_service.__file__}")
except ImportError as e:
    print(f"❌ Failed to import rss_service: {e}")
except Exception as e:
    print(f"❌ Error importing rss_service: {e}")
