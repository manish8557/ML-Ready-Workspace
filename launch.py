#!/usr/bin/env python3
"""
Platform-independent ML Workspace Launcher
Automatically starts Docker containers and opens browser tabs
"""

import os
import sys
import time
import webbrowser
import subprocess
import platform
from pathlib import Path
import threading
import re

class ProgressIndicator:
    """Custom progress indicator with spinning animation"""
    
    def __init__(self):
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0
        self.running = False
        self.thread = None
    
    def _spin(self, message):
        while self.running:
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            sys.stdout.write(f"\r{self.spinner_chars[self.spinner_index]} {message}...")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def start(self, message):
        """Start the spinner with a message"""
        self.running = True
        self.thread = threading.Thread(target=self._spin, args=(message,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, success=True, message=""):
        """Stop the spinner and show result"""
        self.running = False
        if self.thread:
            self.thread.join()
        
        if success:
            sys.stdout.write(f"\r✅ {message}\n")
        else:
            sys.stdout.write(f"\r❌ {message}\n")
        sys.stdout.flush()

def print_header():
    """Print a nice header"""
    header = """
🤖 ML WORKSPACE LAUNCHER
─────────────────────────────────────────
    """
    print(header)

def print_step(step_number, title):
    """Print a step header"""
    print(f"\n📝 Step {step_number}: {title}")
    print("─" * (len(title) + 10))

def check_docker():
    """Check if Docker is running"""
    progress = ProgressIndicator()
    progress.start("Checking Docker installation")
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            progress.stop(True, f"Docker is installed ({result.stdout.strip()})")
            return True
        else:
            progress.stop(False, "Docker is not installed or not running")
            return False
    except FileNotFoundError:
        progress.stop(False, "Docker is not installed")
        return False

def check_docker_compose():
    """Check if docker-compose is available"""
    progress = ProgressIndicator()
    progress.start("Checking Docker Compose")
    
    try:
        # Try docker-compose (older)
        result = subprocess.run(['docker-compose', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            progress.stop(True, f"Docker Compose available ({result.stdout.strip()})")
            return True
        else:
            # Try docker compose (newer)
            result = subprocess.run(['docker', 'compose', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                progress.stop(True, f"Docker Compose available ({result.stdout.strip()})")
                return True
            progress.stop(False, "Docker Compose is not available")
            return False
    except FileNotFoundError:
        progress.stop(False, "Docker Compose is not available")
        return False

def stop_existing_containers():
    """Stop any existing containers"""
    progress = ProgressIndicator()
    progress.start("Stopping existing containers")
    
    result = subprocess.run(['docker-compose', 'down'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        progress.stop(True, "Stopped existing containers")
    else:
        progress.stop(False, "Failed to stop containers")

def build_containers():
    """Build Docker containers with progress"""
    print("🔨 Building Docker images...")
    
    # Use subprocess with real-time output
    process = subprocess.Popen(['docker-compose', 'build', '--no-cache'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             text=True,
                             bufsize=1,
                             universal_newlines=True)
    
    # Show progress with dots
    dot_count = 0
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Show building progress with rotating dots
            dot_chars = ["   ", ".  ", ".. ", "..."]
            dot_count = (dot_count + 1) % len(dot_chars)
            sys.stdout.write(f"\r🔄 Building{dot_chars[dot_count]}")
            sys.stdout.flush()
    
    return_code = process.poll()
    if return_code == 0:
        print(f"\r✅ Docker images built successfully!")
        return True
    else:
        print(f"\r❌ Docker build failed!")
        return False

def start_containers():
    """Start containers with progress"""
    progress = ProgressIndicator()
    progress.start("Starting containers")
    
    result = subprocess.run(['docker-compose', 'up', '-d'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        progress.stop(True, "Containers started successfully")
        return True
    else:
        progress.stop(False, "Failed to start containers")
        print(f"Error: {result.stderr}")
        return False

def wait_for_services():
    """Wait for services to be ready with progress bar"""
    print("\n⏳ Waiting for services to start...")
    
    total_wait = 15
    for i in range(total_wait):
        progress = (i + 1) / total_wait * 100
        bar_length = 30
        filled_length = int(bar_length * (i + 1) // total_wait)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r🔄 [{bar}] {progress:.0f}% ({i+1}/{total_wait}s)')
        sys.stdout.flush()
        time.sleep(1)
    
    print(f"\r✅ Services should be ready now!{' ' * 50}")

def extract_jupyter_token():
    """Extract Jupyter token from docker logs"""
    progress = ProgressIndicator()
    progress.start("Looking for Jupyter authentication token")
    
    # Get recent logs
    result = subprocess.run(['docker-compose', 'logs', '--tail=50', 'ml-workspace'], 
                          capture_output=True, text=True)
    
    # Look for token in logs
    token_pattern = r'token=([a-f0-9]+)'
    matches = re.findall(token_pattern, result.stdout)
    
    if matches:
        token = matches[-1]  # Get the most recent token
        jupyter_url = f"http://localhost:8888/lab?token={token}"
        progress.stop(True, f"Jupyter token found: {token}")
        return token, jupyter_url
    else:
        progress.stop(False, "No token found in logs, Jupyter might not require authentication")
        return None, "http://localhost:8888"

def handle_jupyter_authentication():
    """Handle Jupyter authentication by showing token to user"""
    print("\n🔐 Jupyter Authentication Required")
    print("─" * 35)
    
    token, jupyter_url = extract_jupyter_token()
    
    if token:
        print(f"📋 Jupyter Token: {token}")
        print(f"🌐 Jupyter URL: {jupyter_url}")
        print("\nPlease follow these steps:")
        print("1. 📱 Open your browser to: http://localhost:8888")
        print("2. 🔑 When prompted, enter this token:")
        print(f"   {token}")
        print("3. ✅ Click 'Log in' or 'Submit'")
        print("4. 🚀 You'll be redirected to Jupyter Lab")
        
        # Ask user to confirm they've entered the token
        print("\n" + "─" * 50)
        input("Press Enter AFTER you have successfully logged into Jupyter Lab... ")
        print("✅ Great! Continuing with TensorBoard setup...")
        
        return True
    else:
        print("❓ No authentication token found.")
        print("💡 Jupyter might be accessible without authentication.")
        print("🌐 Try opening: http://localhost:8888")
        
        response = input("\nCan you access Jupyter Lab? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        else:
            print("🔧 Let's try to fix Jupyter authentication...")
            return False

def check_service_health():
    """Check if services are running properly"""
    print("\n🔍 Checking service health...")
    
    services_checked = 0
    services_healthy = 0
    
    # Check containers status
    progress = ProgressIndicator()
    progress.start("Checking container status")
    
    result = subprocess.run(['docker-compose', 'ps'], 
                          capture_output=True, text=True)
    progress.stop(True, "Container status checked")
    
    print("\n📊 Container Status:")
    print("─" * 40)
    for line in result.stdout.split('\n'):
        if 'ml-workspace' in line:
            print(f"   {line}")
    
    # Check Jupyter - with better error handling
    progress.start("Checking Jupyter Lab")
    try:
        import requests
        response = requests.get('http://localhost:8888/lab', timeout=10)
        if response.status_code == 200:
            progress.stop(True, "Jupyter Lab is running on http://localhost:8888")
            services_healthy += 1
        elif response.status_code == 403:
            progress.stop(False, "Jupyter requires authentication token")
            # Let user handle authentication
            if handle_jupyter_authentication():
                services_healthy += 1
            else:
                progress.stop(False, "Jupyter authentication failed")
        else:
            progress.stop(False, f"Jupyter returned status {response.status_code}")
    except Exception as e:
        progress.stop(False, f"Jupyter not ready yet: {str(e)}")
    services_checked += 1
    
    # Check TensorBoard
    progress.start("Checking TensorBoard")
    try:
        import requests
        response = requests.get('http://localhost:6006', timeout=10)
        if response.status_code == 200:
            progress.stop(True, "TensorBoard is running on http://localhost:6006")
            services_healthy += 1
        else:
            progress.stop(False, f"TensorBoard returned status {response.status_code}")
    except Exception as e:
        progress.stop(False, f"TensorBoard not ready yet: {str(e)}")
    services_checked += 1
    
    return services_healthy == services_checked

def open_browser_tabs():
    """Open browser tabs for Jupyter and TensorBoard"""
    print("\n🌐 Opening browser tabs...")
    
    # Get Jupyter URL with token
    token, jupyter_url = extract_jupyter_token()
    
    if token:
        print(f"🔑 Jupyter requires token: {token}")
        print("💡 The token will be automatically filled if the browser supports it")
    
    # Open Jupyter
    progress = ProgressIndicator()
    progress.start("Opening Jupyter Lab")
    webbrowser.open('http://localhost:8888')
    time.sleep(2)
    progress.stop(True, "Opened Jupyter Lab")
    
    # Wait a bit before opening TensorBoard
    time.sleep(2)
    
    # Open TensorBoard
    progress.start("Opening TensorBoard")
    webbrowser.open('http://localhost:6006')
    progress.stop(True, "Opened TensorBoard")

def show_success_message():
    """Show final success message"""
    # Get the token info
    token, jupyter_url = extract_jupyter_token()
    
    if token:
        access_instructions = f"""
📊 ACCESS YOUR SERVICES:
   • Jupyter Lab:    http://localhost:8888
   • Jupyter Token:  {token}
   • TensorBoard:    http://localhost:6006

💡 ACCESS INSTRUCTIONS:
   1. Go to http://localhost:8888
   2. Enter the token when prompted: {token}
   3. Click 'Log in' to access Jupyter Lab
   4. TensorBoard should work without authentication
"""
    else:
        access_instructions = """
📊 ACCESS YOUR SERVICES:
   • Jupyter Lab:    http://localhost:8888 (no token needed)
   • TensorBoard:    http://localhost:6006
"""
    
    success_msg = f"""
🎉 SUCCESS! ML WORKSPACE IS READY!
─────────────────────────────────────────
{access_instructions}
🔧 MANAGEMENT COMMANDS:
   • Stop:           docker-compose down
   • View logs:      docker-compose logs -f  
   • Restart:        docker-compose restart
   • Status:         docker-compose ps

🐳 CONTAINER ACCESS:
   • Enter container: docker-compose exec ml-workspace bash
   • TensorBoard CLI: tensorboard --logdir=./logs

💡 TIP: Your workspace will keep running in the background.
         Run 'docker-compose down' when you're done working.
    """
    print(success_msg)

def main():
    """Main launcher function"""
    print_header()
    
    # Check prerequisites
    print_step(1, "System Prerequisites")
    if not check_docker():
        sys.exit(1)
    if not check_docker_compose():
        sys.exit(1)
    
    # Build and start services
    print_step(2, "Container Setup")
    stop_existing_containers()
    
    if not build_containers():
        sys.exit(1)
    
    if not start_containers():
        sys.exit(1)
    
    # Wait and check services
    print_step(3, "Service Initialization")
    wait_for_services()
    
    if not check_service_health():
        print("\n⚠️  Some services may not be fully ready yet.")
        print("   They might need a few more seconds to start up.")
    
    # Final setup
    print_step(4, "Final Setup")
    open_browser_tabs()
    show_success_message()
    
    # Show logs option
    try:
        print("\n📋 Showing container logs (Ctrl+C to exit and keep services running):")
        print("─" * 70)
        subprocess.run(['docker-compose', 'logs', '-f', '--tail=20'])
    except KeyboardInterrupt:
        print("\n\n👋 Launcher stopped. Your ML workspace is still running!")
        print("   Remember to run 'docker-compose down' when you're done.")

if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ The 'requests' library is required but not installed.")
        print("   Install it with: pip install requests")
        sys.exit(1)
    
    main()