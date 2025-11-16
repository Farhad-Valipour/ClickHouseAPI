"""
Tests for health check endpoints.
"""

import pytest
from fastapi import status


def test_basic_health_check(client):
    """Test basic health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_readiness_check_healthy(client, mock_db):
    """Test readiness check when database is healthy."""
    response = client.get("/health/ready")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"]["status"] == "up"


def test_readiness_check_unhealthy(client, mock_db):
    """Test readiness check when database is unhealthy."""
    # Mock unhealthy database
    mock_db.health_check.return_value = {
        "status": "down",
        "error": "Connection refused"
    }
    
    response = client.get("/health/ready")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "unhealthy"
    assert data["checks"]["database"]["status"] == "down"


def test_liveness_check(client):
    """Test liveness check endpoint."""
    response = client.get("/health/live")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["status"] == "ok"


def test_health_check_has_correct_structure(client):
    """Test that health check response has correct structure."""
    response = client.get("/health")
    data = response.json()
    
    required_fields = ["status", "version", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_readiness_check_has_correct_structure(client, mock_db):
    """Test that readiness check response has correct structure."""
    response = client.get("/health/ready")
    data = response.json()
    
    required_fields = ["status", "version", "timestamp", "checks"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    assert "database" in data["checks"]
    assert "api" in data["checks"]
