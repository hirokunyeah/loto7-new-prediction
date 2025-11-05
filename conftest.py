"""Pytest configuration and shared fixtures."""
import pytest
import json
import tempfile
import os
from app import create_app
from app.models import Loto7Draw


@pytest.fixture
def app():
    """Create Flask app for testing."""
    # Create temporary file for testing
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
    os.close(temp_fd)
    
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['LOTO7_DATA_FILE'] = temp_path
    
    # Initialize with empty data
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump({'draws': []}, f)
    
    yield app
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_draw_data():
    """Sample Loto7 draw data."""
    return {
        'id': '第650回',
        'date': '2024-10-31',
        'main': [1, 8, 10, 14, 25, 33, 35],
        'bonus': [12, 21]
    }


@pytest.fixture
def sample_draw(sample_draw_data):
    """Create sample Loto7Draw object."""
    return Loto7Draw.from_dict(sample_draw_data)


@pytest.fixture
def multiple_draws_data():
    """Multiple sample draws."""
    return {
        'draws': [
            {
                'id': '第650回',
                'date': '2024-10-31',
                'main': [1, 8, 10, 14, 25, 33, 35],
                'bonus': [12, 21]
            },
            {
                'id': '第649回',
                'date': '2024-10-25',
                'main': [12, 22, 23, 26, 33, 35, 37],
                'bonus': [2, 21]
            },
            {
                'id': '第648回',
                'date': '2024-10-18',
                'main': [3, 7, 15, 19, 28, 32, 35],
                'bonus': [9, 30]
            }
        ]
    }


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file."""
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
    os.close(temp_fd)
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def populated_data_file(temp_json_file, multiple_draws_data):
    """Create a temporary JSON file with sample data."""
    with open(temp_json_file, 'w', encoding='utf-8') as f:
        json.dump(multiple_draws_data, f)
    return temp_json_file
