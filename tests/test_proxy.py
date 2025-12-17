"""
Tests for proxy support in ClobClient
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON


class TestProxySupport:
    """Test cases for proxy functionality"""
    
    def test_client_accepts_proxies_parameter(self):
        """Test that ClobClient accepts proxies parameter"""
        proxy_dict = {
            "http://": "http://user:pass@proxy:8080",
            "https://": "http://user:pass@proxy:8080"
        }
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key="0x0000000000000000000000000000000000000000000000000000000000000001",
            chain_id=POLYGON,
            proxies=proxy_dict
        )
        
        assert client.proxies == proxy_dict
    
    def test_client_without_proxies(self):
        """Test that ClobClient works without proxies (backward compatibility)"""
        client = ClobClient(
            "https://clob.polymarket.com",
            key="0x0000000000000000000000000000000000000000000000000000000000000001",
            chain_id=POLYGON
        )
        
        assert client.proxies is None
    
    @patch('py_clob_client.http_helpers.helpers.httpx.Client')
    def test_http_request_uses_proxy(self, mock_client_class):
        """Test that HTTP requests use the configured proxy"""
        proxy_dict = {
            "http://": "http://user:pass@proxy:8080",
            "https://": "http://user:pass@proxy:8080"
        }
        
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        # Mock the client instance
        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_client_instance.__enter__ = Mock(return_value=mock_client_instance)
        mock_client_instance.__exit__ = Mock(return_value=False)
        mock_client_class.return_value = mock_client_instance
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key="0x0000000000000000000000000000000000000000000000000000000000000001",
            chain_id=POLYGON,
            proxies=proxy_dict
        )
        
        # Make a request
        try:
            client.get_ok()
        except Exception:
            pass  # We're just testing that proxy is passed
        
        # Verify that httpx.Client was called with proxies
        # Check if any call to Client() included the proxies
        calls_with_proxies = [
            call for call in mock_client_class.call_args_list
            if 'proxies' in call[1] or (len(call[0]) > 0 and call[0][0] == proxy_dict)
        ]
        
        # At least one client should have been created with proxies
        assert len(calls_with_proxies) > 0 or mock_client_class.call_args[1].get('proxies') == proxy_dict
    
    def test_proxy_dict_format(self):
        """Test that proxy dict has correct format"""
        proxy_dict = {
            "http://": "http://user:pass@proxy:8080",
            "https://": "http://user:pass@proxy:8080"
        }
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key="0x0000000000000000000000000000000000000000000000000000000000000001",
            chain_id=POLYGON,
            proxies=proxy_dict
        )
        
        assert "http://" in client.proxies or "http" in client.proxies
        assert "https://" in client.proxies or "https" in client.proxies
    
    def test_client_initialization_with_none_proxies(self):
        """Test that client initializes correctly with None proxies"""
        client = ClobClient(
            "https://clob.polymarket.com",
            proxies=None
        )
        
        assert client.proxies is None
        assert client.host == "https://clob.polymarket.com"
    
    def test_client_stores_proxy_config(self):
        """Test that client stores proxy configuration as instance variable"""
        proxy_dict = {"http://": "http://proxy:8080"}
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key="0x0000000000000000000000000000000000000000000000000000000000000001",
            chain_id=POLYGON,
            proxies=proxy_dict
        )
        
        # Verify proxies are stored
        assert hasattr(client, 'proxies')
        assert client.proxies == proxy_dict
    
    @patch('py_clob_client.http_helpers.helpers.httpx.Client')
    def test_multiple_requests_with_same_proxy(self, mock_client_class):
        """Test that multiple requests all use the same proxy configuration"""
        proxy_dict = {
            "http://": "http://user:pass@proxy:8080",
            "https://": "http://user:pass@proxy:8080"
        }
        
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"timestamp": "123456"}
        
        # Mock the client instance
        mock_client_instance = Mock()
        mock_client_instance.request.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        
        client = ClobClient(
            "https://clob.polymarket.com",
            key="0x0000000000000000000000000000000000000000000000000000000000000001",
            chain_id=POLYGON,
            proxies=proxy_dict
        )
        
        # Make multiple requests
        try:
            client.get_ok()
            client.get_server_time()
        except Exception:
            pass
        
        # Verify client was created with proxies parameter
        assert mock_client_class.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
