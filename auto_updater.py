import os
import time
import subprocess

FILE_TO_WATCH = r'D:\translated_large.xlsx'

def get_mtime():
    """Get the last modified time of the file."""
    try:
        return os.path.getmtime(FILE_TO_WATCH)
    except OSError:
        return 0

def main():
    print(f"👀 Auto-Updater started. Monitoring:\n{FILE_TO_WATCH}")
    print("Keep this window open in the background. Press Ctrl+C to stop.\n")
    
    last_mtime = get_mtime()
    
    while True:
        time.sleep(3) # Check the file every 3 seconds
        current_mtime = get_mtime()
        
        # If the file's modified time changes, it means it was saved/updated
        if current_mtime != last_mtime:
            print(f"[{time.strftime('%H:%M:%S')}] 🔄 Change detected in the Excel dataset!")
            print("Running sync and deploying updates...")
            
            try:
                # Run your sync script which now auto-pushes to GitHub
                subprocess.run(['python', 'sync_tenders.py'], check=True)
                last_mtime = current_mtime # Reset the watch time
                print("✅ Update successfully pushed to the live dashboard! Resuming watch...\n")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error during sync/deployment: {e}\nResuming watch...")
            except Exception as e:
                print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
