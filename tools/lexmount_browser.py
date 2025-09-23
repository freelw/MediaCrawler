import os
import requests
import json
from typing import Optional, Dict, Any
from urllib.parse import urljoin


class Session:
    """Represents a browser session"""
    
    def __init__(self, session_id: str, browser: 'Browser'):
        self.id = session_id
        self._browser = browser
        self.webSocketDebuggerUrl = None
        self._get_web_socket_debugger_url()
    
    def _get_web_socket_debugger_url(self):
        """Get the WebSocket debugger URL for this session"""
        try:
            url = urljoin(self._browser.base_url, '/json/version')
            params = {'session_id': self.id}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            full_ws_url = data.get('webSocketDebuggerUrl')
            
            if full_ws_url:
                # Extract only the path part from the WebSocket URL
                from urllib.parse import urlparse
                parsed = urlparse(full_ws_url)
                self.webSocketDebuggerUrl = parsed.path
            else:
                self.webSocketDebuggerUrl = None
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Failed to get WebSocket debugger URL: {e}")
            self.webSocketDebuggerUrl = None
    
    def __str__(self):
        return f"Session(id='{self.id}', webSocketDebuggerUrl='{self.webSocketDebuggerUrl}')"
    
    def __repr__(self):
        return self.__str__()


class Sessions:
    """Manages browser sessions"""
    
    def __init__(self, browser: 'Browser'):
        self._browser = browser
    
    def create(self, project_id: str) -> Session:
        """
        Create a new browser session
        
        Args:
            project_id: The project ID for the session
            
        Returns:
            Session: A new browser session
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = urljoin(self._browser.base_url, '/instance')
        
        payload = {
            'project_id': project_id,
            'api_key': self._browser.api_key
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            session_id = data.get('session_id')
            
            if not session_id:
                raise ValueError("No session_id returned from API")
            
            return Session(session_id, self._browser)
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Failed to create session: {e}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid response from API: {e}")


class Browser:
    """Main browser client for Lexmount Browser API"""
    
    def __init__(self, api_key: str, base_url: str = "https://freelw.cc"):
        """
        Initialize the browser client
        
        Args:
            api_key: Your API key for authentication
            base_url: Base URL for the API (default: https://freelw.cc)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.sessions = Sessions(self)
    
    def __str__(self):
        return f"Browser(api_key='{self.api_key[:8]}...', base_url='{self.base_url}')"
    
    def __repr__(self):
        return self.__str__()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the API
        
        Returns:
            Dict containing health status information
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = urljoin(self.base_url, '/health')
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Health check failed: {e}")
    
    def get_session_logs(self, session_id: str) -> Dict[str, Any]:
        """
        Get logs for a specific session
        
        Args:
            session_id: The session ID to get logs for
            
        Returns:
            Dict containing session logs
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = urljoin(self.base_url, f'/logs/{session_id}')
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Failed to get session logs: {e}")
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a browser session
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            bool: True if successful
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = urljoin(self.base_url, '/instance')
        
        params = {
            'session_id': session_id
        }
        
        try:
            response = requests.delete(url, params=params)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Failed to delete session: {e}")


# For backward compatibility and easier imports
LexmountBrowser = Browser
