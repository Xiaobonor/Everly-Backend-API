#!/usr/bin/env python
"""
Everly API Test Client

This script provides a command-line tool for testing the Everly backend API.
It supports automatic, manual, and frontend simulation operations.
"""

import argparse
import json
import os
import sys
import time
import webbrowser
import http.server
import socketserver
import urllib.parse
import threading
import secrets
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

# Global variables
console = Console()
API_BASE_URL = ""
ACCESS_TOKEN = ""
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_config.json")
AUTH_CODE = None
STATE = None
OAUTH_PORT = 8085  # Local callback server port

# OAuth settings
OAUTH_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
# Provide two redirect URI options
OAUTH_DEFAULT_REDIRECT_URI = f"http://localhost:8000/api/v1/auth/google/callback"  # Backend default redirect URI
OAUTH_LOCAL_REDIRECT_URI = f"http://localhost:{OAUTH_PORT}/oauth/callback"  # Local server redirect URI
OAUTH_REDIRECT_URI = OAUTH_DEFAULT_REDIRECT_URI  # Default to using backend redirect URI

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for OAuth callbacks"""
    
    def do_GET(self):
        """Handle GET requests"""
        global AUTH_CODE, STATE
        
        # Parse URL and query parameters
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # Check if the path is the callback path
        if parsed_path.path == "/oauth/callback":
            # Get authorization code and state
            if "code" in query_params and "state" in query_params:
                auth_code = query_params["code"][0]
                received_state = query_params["state"][0]
                
                # Verify state to prevent CSRF attacks
                if received_state == STATE:
                    AUTH_CODE = auth_code
                    response_html = """
                    <html>
                    <head>
                        <title>Everly API Authentication Success</title>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .success { color: green; font-size: 24px; margin-bottom: 20px; }
                            .info { margin-bottom: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="success">✓ Authorization Successful!</div>
                        <div class="info">You have successfully authorized the Everly API Test Client.</div>
                        <div>You can now close this window and return to the test client.</div>
                    </body>
                    </html>
                    """
                else:
                    AUTH_CODE = None
                    response_html = """
                    <html>
                    <head>
                        <title>Everly API Authentication Failed</title>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .error { color: red; font-size: 24px; margin-bottom: 20px; }
                            .info { margin-bottom: 20px; }
                        </style>
                    </head>
                    <body>
                        <div class="error">✗ Authentication Failed!</div>
                        <div class="info">State validation failed, possible CSRF attack.</div>
                        <div>Please close this window and try again.</div>
                    </body>
                    </html>
                    """
            else:
                # Missing parameters
                AUTH_CODE = None
                response_html = """
                <html>
                <head>
                    <title>Everly API Authentication Failed</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; font-size: 24px; margin-bottom: 20px; }
                        .info { margin-bottom: 20px; }
                    </style>
                </head>
                <body>
                    <div class="error">✗ Authentication Failed!</div>
                    <div class="info">Missing required authentication parameters.</div>
                    <div>Please close this window and try again.</div>
                </body>
                </html>
                """
            
            # Send HTML response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response_html.encode())
            
            # Notify server to stop
            self.server.server_close()
        else:
            # Return 404 for other paths
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def start_oauth_callback_server() -> None:
    """Start local OAuth callback server"""
    # Use ThreadingTCPServer to allow server to run in the background
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", OAUTH_PORT), OAuthCallbackHandler) as httpd:
        console.print(f"\n[green]Local OAuth callback server started at http://localhost:{OAUTH_PORT}[/green]")
        console.print("[yellow]Waiting for Google authorization callback...[/yellow]")
        console.print("Please complete the Google authorization flow in your browser")
        
        # Run server until callback is received or timeout
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait up to 5 minutes
        timeout = time.time() + 300
        while time.time() < timeout and AUTH_CODE is None and server_thread.is_alive():
            time.sleep(1)
        
        # Stop server
        httpd.shutdown()
        server_thread.join()

def generate_google_auth_url() -> str:
    """Generate Google OAuth authorization URL"""
    global STATE
    
    # Generate a random state value to prevent CSRF attacks
    STATE = secrets.token_urlsafe(16)
    
    # Build authorization URL
    scope = "email profile"
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": OAUTH_CLIENT_ID,
        "redirect_uri": OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": scope,
        "state": STATE,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # Add parameters to URL
    query_string = urllib.parse.urlencode(params)
    return f"{auth_url}?{query_string}"

def get_client_id_from_env() -> Tuple[bool, str]:
    """從環境變量或配置文件中獲取客戶端 ID"""
    global OAUTH_CLIENT_ID
    
    # 首先檢查環境變量
    if OAUTH_CLIENT_ID:
        return True, OAUTH_CLIENT_ID
    
    # 然後檢查配置文件
    config = load_config()
    if "google_client_id" in config:
        OAUTH_CLIENT_ID = config["google_client_id"]
        return True, OAUTH_CLIENT_ID
    
    return False, ""

def google_login() -> None:
    """執行 Google 登入流程，支援兩種認證方式"""
    global ACCESS_TOKEN, AUTH_CODE, OAUTH_CLIENT_ID, OAUTH_REDIRECT_URI
    
    console.print("\n[bold cyan]Google Login Process[/bold cyan]")
    
    # 選擇認證模式
    console.print("\n[bold]Please choose authentication mode:[/bold]")
    console.print("1. Direct Mode - Use backend defined callback (Recommended)")
    console.print("2. Local Server Mode - Use local server to receive callback (May require additional configuration)")
    
    auth_mode = Prompt.ask("Choose mode", choices=["1", "2"], default="1")
    
    if auth_mode == "1":
        # 直接模式 - 使用後端定義的回調
        OAUTH_REDIRECT_URI = OAUTH_DEFAULT_REDIRECT_URI
        direct_oauth_flow()
    else:
        # 本地伺服器模式
        OAUTH_REDIRECT_URI = OAUTH_LOCAL_REDIRECT_URI
        local_server_oauth_flow()

def direct_oauth_flow() -> None:
    """OAuth flow using the backend-defined callback URI directly"""
    global ACCESS_TOKEN, OAUTH_CLIENT_ID
    
    console.print("\n[bold cyan]Google Login (Direct Mode)[/bold cyan]")
    console.print("This will guide you to complete Google authorization in your browser, then enter authorization code or redirect URL")
    
    # Get client ID
    has_client_id, client_id = get_client_id_from_env()
    if not has_client_id:
        OAUTH_CLIENT_ID = Prompt.ask("Please enter Google OAuth Client ID")
        # Save to config file
        config = load_config()
        config["google_client_id"] = OAUTH_CLIENT_ID
        save_config(config)
    
    console.print(f"\nUsing Client ID: [cyan]{OAUTH_CLIENT_ID}[/cyan]")
    console.print(f"Redirect URI: [cyan]{OAUTH_REDIRECT_URI}[/cyan]")
    
    # Build Google authorization URL
    auth_url = generate_google_auth_url()
    
    # Open browser
    console.print("\nPlease complete Google authorization in your browser")
    if Confirm.ask("Do you want to automatically open your browser for Google authorization?", default=True):
        webbrowser.open(auth_url)
    else:
        console.print(f"\nPlease manually visit the following URL to authorize:")
        console.print(f"[link={auth_url}]{auth_url}[/link]")
    
    console.print("\n[yellow]After authorization, your browser will redirect to callback URL (may display 404 page)[/yellow]")
    console.print("[bold cyan]Choose input method:[/bold cyan]")
    console.print("1. Enter full redirect URL (Recommended, automatically extracts authorization code)")
    console.print("2. Enter only authorization code (code=... part)")
    
    input_mode = Prompt.ask("Choose input method", choices=["1", "2"], default="1")
    
    if input_mode == "1":
        # User inputs full URL, automatically extract the authorization code
        redirect_url = Prompt.ask("Please paste full redirect URL (contains code=...)")
        # Parse URL to get authorization code
        try:
            parsed_url = urllib.parse.urlparse(redirect_url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if "code" in query_params:
                auth_code = query_params["code"][0]
                console.print(f"[green]✓ Authorization code extracted from URL[/green]")
            else:
                console.print("[red]✗ Unable to extract authorization code from URL[/red]")
                auth_code = Prompt.ask("Please enter authorization code directly")
        except Exception as e:
            console.print(f"[red]✗ Error parsing URL: {e}[/red]")
            auth_code = Prompt.ask("Please enter authorization code directly")
    else:
        # User directly inputs authorization code
        auth_code = Prompt.ask("Please enter the authorization code (code=... part)")
    
    # Use authorization code to get access token
    console.print("\nUsing authorization code to get access token...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/google",
            json={"code": auth_code},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            ACCESS_TOKEN = data.get("data", {}).get("access_token", "")
            
            if ACCESS_TOKEN:
                console.print("[green]✓ Access token obtained successfully![/green]")
                
                # Save token
                config = load_config()
                config["access_token"] = ACCESS_TOKEN
                save_config(config)
                
                # Validate token
                test_token()
            else:
                console.print("[red]✗ No access token in response![/red]")
                console.print(response.text)
        else:
            console.print(f"[red]✗ Failed to get access token! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")

def local_server_oauth_flow() -> None:
    """OAuth flow using a local server"""
    global ACCESS_TOKEN, AUTH_CODE, OAUTH_CLIENT_ID
    
    console.print("\n[bold cyan]Google Login (Local Server Mode)[/bold cyan]")
    console.print("[yellow]Note: This mode requires adding the following redirect URI in Google Developer Console:[/yellow]")
    console.print(f"[bold]{OAUTH_REDIRECT_URI}[/bold]")
    
    # Get client ID
    has_client_id, client_id = get_client_id_from_env()
    if not has_client_id:
        OAUTH_CLIENT_ID = Prompt.ask("Please enter Google OAuth Client ID")
        # Save to config file
        config = load_config()
        config["google_client_id"] = OAUTH_CLIENT_ID
        save_config(config)
    
    console.print(f"\nUsing Client ID: [cyan]{OAUTH_CLIENT_ID}[/cyan]")
    console.print(f"Redirect URI: [cyan]{OAUTH_REDIRECT_URI}[/cyan]")
    
    if not Confirm.ask("Are you sure to continue? You must ensure that the redirect URI is correctly set up in Google Developer Console"):
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    
    # Step 1: Build Google authorization URL
    console.print("\n1. Generate Google Authorization URL")
    auth_url = generate_google_auth_url()
    
    # Step 2: Start callback server
    console.print("\n2. Start local callback server")
    AUTH_CODE = None
    server_thread = threading.Thread(target=start_oauth_callback_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Step 3: Open browser and guide user through authorization
    console.print("\n3. Open browser for Google authorization")
    if Confirm.ask("Do you want to automatically open your browser for Google authorization?", default=True):
        webbrowser.open(auth_url)
    else:
        console.print(f"\nPlease manually visit the following URL to authorize:")
        console.print(f"[link={auth_url}]{auth_url}[/link]")
    
    # Wait for callback server to receive authorization code
    console.print("\n[yellow]Waiting for Google authorization callback...[/yellow]")
    server_thread.join(timeout=300)  # Wait up to 5 minutes
    
    # Check if authorization code was received
    if AUTH_CODE is None:
        console.print("\n[red]✗ Unable to get authorization code, login failed![/red]")
        return
    
    console.print("\n[green]✓ Authorization code obtained![/green]")
    
    # Step 4: Use authorization code to call backend API for access token
    console.print("\n4. Using authorization code to get access token")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/auth/google",
            json={"code": AUTH_CODE},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            ACCESS_TOKEN = data.get("data", {}).get("access_token", "")
            
            if ACCESS_TOKEN:
                console.print("[green]✓ Access token obtained successfully![/green]")
                
                # Save token
                config = load_config()
                config["access_token"] = ACCESS_TOKEN
                save_config(config)
                
                # Validate token
                test_token()
            else:
                console.print("[red]✗ No access token in response![/red]")
                console.print(response.text)
        else:
            console.print(f"[red]✗ Failed to get access token! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
    
    # Clear authorization code
    AUTH_CODE = None


def save_config(config: Dict[str, Any]) -> None:
    """保存配置到文件"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_config() -> Dict[str, Any]:
    """從文件加載配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def setup_api_url() -> str:
    """Set up API base URL"""
    global API_BASE_URL
    
    config = load_config()
    default_url = config.get("api_url", "http://localhost:8000")
    
    API_BASE_URL = Prompt.ask("Please enter backend API base URL", default=default_url)
    
    # Remove trailing slash
    if API_BASE_URL.endswith("/"):
        API_BASE_URL = API_BASE_URL[:-1]
    
    # Save to config
    config["api_url"] = API_BASE_URL
    save_config(config)
    
    return API_BASE_URL


def get_headers() -> Dict[str, str]:
    """獲取 HTTP 請求頭"""
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}" if ACCESS_TOKEN else "",
        "Content-Type": "application/json"
    }


def test_token() -> bool:
    """Test if access token is valid"""
    global ACCESS_TOKEN
    
    if not ACCESS_TOKEN:
        console.print("[yellow]No access token set, please log in[/yellow]")
        return False
    
    console.print("\n[bold cyan]Validating access token...[/bold cyan]")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/auth/me",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            user_info = response.json()
            
            # Extract user data, handle different response structures
            user_data = None
            if "data" in user_info:
                user_data = user_info.get("data", {})
            else:
                # If no data field, response may directly contain user data
                user_data = user_info
            
            if user_data and "full_name" in user_data:
                console.print(f"[green]✓ Token valid! Logged in as: {user_data.get('full_name')}[/green]")
                return True
            else:
                console.print(f"[green]✓ Token valid![/green]")
                return True
        else:
            console.print(f"[red]✗ Token invalid! Status code: {response.status_code}[/red]")
            console.print(response.text)
            ACCESS_TOKEN = ""
            return False
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        # Output more detailed error information
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def get_user_info() -> None:
    """Get current user information"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Getting user information...[/bold cyan]")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/users/me",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            user_info = response.json()
            
            # Debug output of original response
            console.print("[dim]Original response:[/dim]")
            console.print(user_info)
            
            # Extract user data, handle different response structures
            user_data = None
            if "data" in user_info:
                user_data = user_info.get("data", {})
            else:
                # If no data field, response may directly contain user data
                user_data = user_info
            
            if not user_data:
                console.print("[yellow]Warning: No user data found in response[/yellow]")
                return
                
            table = Table(title="User Information")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            # Iterate and display user data
            for key, value in user_data.items():
                if value is not None:  # Only show non-empty values
                    if isinstance(value, (dict, list)):
                        table.add_row(key, json.dumps(value, ensure_ascii=False))
                    else:
                        table.add_row(key, str(value))
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to get user information! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        # Output more detailed error information
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def get_diary_entries() -> None:
    """Get diary entries list"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Getting diary entries list...[/bold cyan]")
    
    try:
        page = int(Prompt.ask("Page", default="1"))
        limit = int(Prompt.ask("Entries per page", default="10"))
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/diaries?page={page}&limit={limit}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            console.print("[dim]Original response:[/dim]")
            console.print(resp_data)
            
            # Handle different response structures
            data = None
            entries = []
            total = 0
            
            # If response contains a data field
            if isinstance(resp_data, dict) and "data" in resp_data:
                data = resp_data.get("data", {})
                if isinstance(data, dict):
                    entries = data.get("items", [])
                    total = data.get("total", 0)
                else:
                    entries = data if isinstance(data, list) else []
                    total = len(entries)
            # If response is directly a list of entries
            elif isinstance(resp_data, list):
                entries = resp_data
                total = len(entries)
            
            console.print(f"Total {total} diary entries, displaying page {page} (entries per page {limit})")
            
            if not entries:
                console.print("[yellow]No diary entries found[/yellow]")
                return
            
            table = Table(title="Diary Entries List")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Created Time", style="blue")
            table.add_column("Tags", style="magenta")
            
            for entry in entries:
                created_at = entry.get("created_at", "")
                if created_at and isinstance(created_at, str) and "T" in created_at:
                    created_at = created_at.split("T")[0]
                
                tags = entry.get("tags", [])
                tags_str = ", ".join(tags) if tags else ""
                
                table.add_row(
                    str(entry.get("id", "")),
                    entry.get("title", ""),
                    created_at,
                    tags_str
                )
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to get diary entries! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def create_diary_entry() -> None:
    """Create new diary entry"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Creating new diary entry...[/bold cyan]")
    
    try:
        title = Prompt.ask("Title")
        content = Prompt.ask("Content")
        tags_input = Prompt.ask("Tags (comma separated)", default="")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        payload = {
            "title": title,
            "content": content,
            "content_type": "text",
            "tags": tags
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/diaries",
            headers=get_headers(),
            json=payload
        )
        
        if response.status_code in (200, 201):
            resp_data = response.json()
            console.print("[green]✓ Diary entry created successfully![/green]")
            
            # Handle different response structures
            entry = {}
            if isinstance(resp_data, dict):
                if "data" in resp_data:
                    entry = resp_data.get("data", {})
                else:
                    entry = resp_data
            
            table = Table(title="New Diary Entry")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in entry.items():
                if value is not None:  # Only show non-empty values
                    if isinstance(value, (dict, list)):
                        table.add_row(key, json.dumps(value, ensure_ascii=False))
                    else:
                        table.add_row(key, str(value))
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to create diary entry! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def get_diary_entry_detail() -> None:
    """Get diary entry detail"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Getting diary entry detail...[/bold cyan]")
    
    try:
        entry_id = Prompt.ask("Please enter diary entry ID")
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            console.print("[dim]Original response:[/dim]")
            console.print(resp_data)
            
            # Handle different response structures
            entry = {}
            if isinstance(resp_data, dict):
                if "data" in resp_data:
                    entry = resp_data.get("data", {})
                else:
                    entry = resp_data
            
            table = Table(title="Diary Entry Detail")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in entry.items():
                if value is not None:  # Only show non-empty values
                    if isinstance(value, (dict, list)):
                        table.add_row(key, json.dumps(value, ensure_ascii=False))
                    else:
                        table.add_row(key, str(value))
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to get diary entry detail! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def update_diary_entry() -> None:
    """Update diary entry"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Updating diary entry...[/bold cyan]")
    
    try:
        entry_id = Prompt.ask("Please enter the ID of the diary entry to update")
        
        # First get current entry
        response = requests.get(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers()
        )
        
        if response.status_code != 200:
            console.print(f"[red]✗ Failed to get diary entry! Status code: {response.status_code}[/red]")
            return
        
        resp_data = response.json()
        
        # Handle different response structures
        current_entry = {}
        if isinstance(resp_data, dict):
            if "data" in resp_data:
                current_entry = resp_data.get("data", {})
            else:
                current_entry = resp_data
        
        title = Prompt.ask("Title", default=current_entry.get("title", ""))
        content = Prompt.ask("Content", default=current_entry.get("content", ""))
        tags_default = ",".join(current_entry.get("tags", []) if isinstance(current_entry.get("tags"), list) else [])
        tags_input = Prompt.ask("Tags (comma separated)", default=tags_default)
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        payload = {
            "title": title,
            "content": content,
            "tags": tags
        }
        
        response = requests.put(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers(),
            json=payload
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            console.print("[green]✓ Diary entry updated successfully![/green]")
            
            # Handle different response structures
            entry = {}
            if isinstance(resp_data, dict):
                if "data" in resp_data:
                    entry = resp_data.get("data", {})
                else:
                    entry = resp_data
            
            table = Table(title="Updated Diary Entry")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in entry.items():
                if value is not None:  # Only show non-empty values
                    if isinstance(value, (dict, list)):
                        table.add_row(key, json.dumps(value, ensure_ascii=False))
                    else:
                        table.add_row(key, str(value))
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to update diary entry! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def delete_diary_entry() -> None:
    """Delete diary entry"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Deleting diary entry...[/bold cyan]")
    
    try:
        entry_id = Prompt.ask("Please enter the ID of the diary entry to delete")
        
        if not Confirm.ask(f"Are you sure to delete diary entry with ID {entry_id}?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
        
        response = requests.delete(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers()
        )
        
        if response.status_code == 204:
            console.print("[green]✓ Diary entry deleted successfully![/green]")
        else:
            console.print(f"[red]✗ Failed to delete diary entry! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")


def search_diary_entries() -> None:
    """Search diary entries"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Searching diary entries...[/bold cyan]")
    
    try:
        query = Prompt.ask("Search keyword", default="")
        tags_input = Prompt.ask("Tags filter (comma separated)", default="")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        start_date = Prompt.ask("Start date (YYYY-MM-DD)", default="")
        end_date = Prompt.ask("End date (YYYY-MM-DD)", default="")
        
        payload = {}
        if query:
            payload["query"] = query
        if tags:
            payload["tags"] = tags
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/diaries/search",
            headers=get_headers(),
            json=payload
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            console.print("[dim]Original response:[/dim]")
            console.print(resp_data)
            
            # Handle different response structures
            entries = []
            total = 0
            
            if isinstance(resp_data, dict):
                if "data" in resp_data:
                    data = resp_data.get("data", {})
                    if isinstance(data, dict):
                        entries = data.get("items", [])
                        total = data.get("total", 0)
                    else:
                        entries = data if isinstance(data, list) else []
                        total = len(entries)
                else:
                    if "items" in resp_data:
                        entries = resp_data.get("items", [])
                        total = resp_data.get("total", len(entries))
                    else:
                        entries = [resp_data]
                        total = 1
            elif isinstance(resp_data, list):
                entries = resp_data
                total = len(entries)
            
            console.print(f"Found {total} matching diary entries")
            
            if not entries:
                console.print("[yellow]No matching diary entries found[/yellow]")
                return
            
            table = Table(title="Search Results")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="green")
            table.add_column("Created Time", style="blue")
            table.add_column("Tags", style="magenta")
            
            for entry in entries:
                created_at = entry.get("created_at", "")
                if created_at and isinstance(created_at, str) and "T" in created_at:
                    created_at = created_at.split("T")[0]
                
                tags = entry.get("tags", [])
                tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
                
                table.add_row(
                    str(entry.get("id", "")),
                    entry.get("title", ""),
                    created_at,
                    tags_str
                )
            
            console.print(table)
        else:
            console.print(f"[red]✗ Failed to search diary entries! Status code: {response.status_code}[/red]")
            console.print(response.text)
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def run_auto_test() -> None:
    """Run automated test"""
    if not test_token():
        return
    
    console.print("\n[bold cyan]Running automated test...[/bold cyan]")
    
    # Test user information
    try:
        console.print("\n[bold]1. Test getting user information[/bold]")
        response = requests.get(
            f"{API_BASE_URL}/api/v1/users/me",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            console.print("[green]✓ User information obtained successfully[/green]")
            
            # Debug output
            resp_data = response.json()
            console.print("[dim]User information:[/dim]")
            if "data" in resp_data:
                console.print(resp_data["data"])
            else:
                console.print(resp_data)
        else:
            console.print(f"[red]✗ Failed to get user information: {response.status_code}[/red]")
            console.print(response.text)
            return
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return
    
    # Create diary entry
    entry_id = None
    try:
        console.print("\n[bold]2. Test creating diary entry[/bold]")
        
        test_title = f"Automated Test Diary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        test_content = "This is a diary entry created by automated test."
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/diaries",
            headers=get_headers(),
            json={
                "title": test_title,
                "content": test_content,
                "content_type": "text",
                "tags": ["Test", "Automated"]
            }
        )
        
        if response.status_code in (200, 201):
            console.print("[green]✓ Diary entry created successfully[/green]")
            
            # Extract ID, handle different response structures
            resp_data = response.json()
            if "data" in resp_data:
                entry_data = resp_data.get("data", {})
            else:
                entry_data = resp_data
                
            entry_id = entry_data.get("id")
            console.print(f"Diary entry ID: {entry_id}")
            
            if not entry_id:
                console.print("[yellow]Warning: Unable to get created diary entry ID[/yellow]")
                return
        else:
            console.print(f"[red]✗ Failed to create diary entry: {response.status_code}[/red]")
            console.print(response.text)
            return
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return
    
    # Get diary details
    try:
        console.print("\n[bold]3. Test getting diary detail[/bold]")
        
        response = requests.get(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            console.print("[green]✓ Diary detail obtained successfully[/green]")
            
            # Debug output
            resp_data = response.json()
            console.print("[dim]Diary detail:[/dim]")
            if "data" in resp_data:
                console.print(resp_data["data"])
            else:
                console.print(resp_data)
        else:
            console.print(f"[red]✗ Failed to get diary detail: {response.status_code}[/red]")
            console.print(response.text)
            return
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return
    
    # Update diary entry
    try:
        console.print("\n[bold]4. Test updating diary entry[/bold]")
        
        updated_title = f"Updated - {test_title}"
        updated_content = f"{test_content} This entry has been updated."
        
        response = requests.put(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers(),
            json={
                "title": updated_title,
                "content": updated_content,
                "tags": ["Test", "Automated", "Updated"]
            }
        )
        
        if response.status_code == 200:
            console.print("[green]✓ Diary entry updated successfully[/green]")
            
            # Debug output
            resp_data = response.json()
            console.print("[dim]Updated diary:[/dim]")
            if "data" in resp_data:
                console.print(resp_data["data"])
            else:
                console.print(resp_data)
        else:
            console.print(f"[red]✗ Failed to update diary entry: {response.status_code}[/red]")
            console.print(response.text)
            return
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return
    
    # Delete diary entry
    try:
        console.print("\n[bold]5. Test deleting diary entry[/bold]")
        
        response = requests.delete(
            f"{API_BASE_URL}/api/v1/diaries/{entry_id}",
            headers=get_headers()
        )
        
        if response.status_code == 204:
            console.print("[green]✓ Diary entry deleted successfully[/green]")
        else:
            console.print(f"[red]✗ Failed to delete diary entry: {response.status_code}[/red]")
            console.print(response.text)
            return
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return
    
    console.print("\n[bold green]✓ All automated tests passed![/bold green]")


def main_menu() -> None:
    """Display main menu"""
    while True:
        console.print("\n[bold]===== Everly API Test Client =====[/bold]")
        console.print(f"Backend API URL: [cyan]{API_BASE_URL}[/cyan]")
        console.print(f"Authentication status: [{'green' if ACCESS_TOKEN else 'red'}]{'Logged in' if ACCESS_TOKEN else 'Not logged in'}[/{'green' if ACCESS_TOKEN else 'red'}]")
        
        console.print("\n[bold]Menu options:[/bold]")
        console.print("1. Set backend API URL")
        console.print("2. Google Login")
        console.print("3. Get user information")
        console.print("4. Get diary entries list")
        console.print("5. Create new diary entry")
        console.print("6. Get diary entry detail")
        console.print("7. Update diary entry")
        console.print("8. Delete diary entry")
        console.print("9. Search diary entries")
        console.print("10. Run automated test")
        console.print("0. Exit")
        
        choice = Prompt.ask("Please choose", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        
        if choice == "0":
            console.print("[bold green]Thank you for using Everly API Test Client![/bold green]")
            break
        elif choice == "1":
            setup_api_url()
        elif choice == "2":
            google_login()
        elif choice == "3":
            get_user_info()
        elif choice == "4":
            get_diary_entries()
        elif choice == "5":
            create_diary_entry()
        elif choice == "6":
            get_diary_entry_detail()
        elif choice == "7":
            update_diary_entry()
        elif choice == "8":
            delete_diary_entry()
        elif choice == "9":
            search_diary_entries()
        elif choice == "10":
            run_auto_test()


def main() -> None:
    """Main function"""
    global API_BASE_URL, ACCESS_TOKEN
    
    parser = argparse.ArgumentParser(description="Everly API Test Client")
    parser.add_argument("--url", help="Backend API URL")
    parser.add_argument("--token", help="Access token")
    parser.add_argument("--autotest", action="store_true", help="Run automated test")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    API_BASE_URL = args.url or config.get("api_url", "")
    ACCESS_TOKEN = args.token or config.get("access_token", "")
    
    # If API URL is not set, prompt user to input
    if not API_BASE_URL:
        setup_api_url()
    
    # Run automated test or show main menu
    if args.autotest:
        run_auto_test()
    else:
        main_menu()


if __name__ == "__main__":
    main() 