"""Tests for DataService."""
import pytest
import json
import os
from unittest.mock import Mock, patch, mock_open
from app.services.data_service import DataService
from app.models import Loto7Draw


@pytest.mark.unit
class TestDataService:
    """Test DataService functionality."""
    
    def test_init(self, temp_json_file):
        """Test initialization."""
        service = DataService(temp_json_file)
        assert service.data_file_path == temp_json_file
    
    def test_load_draws_empty_file(self, temp_json_file):
        """Test loading from empty file."""
        with open(temp_json_file, 'w') as f:
            json.dump({'draws': []}, f)
        
        service = DataService(temp_json_file)
        draws = service.load_draws()
        assert draws == []
    
    def test_load_draws_with_data(self, populated_data_file):
        """Test loading draws from populated file."""
        service = DataService(populated_data_file)
        draws = service.load_draws()
        assert len(draws) == 3
        assert draws[0].id == '第650回'
        assert draws[1].id == '第649回'
        assert draws[2].id == '第648回'
    
    def test_load_draws_file_not_found(self):
        """Test loading from non-existent file."""
        service = DataService('/nonexistent/path/file.json')
        draws = service.load_draws()
        assert draws == []
    
    @patch('builtins.open', mock_open(read_data='invalid json'))
    def test_load_draws_invalid_json(self):
        """Test loading invalid JSON."""
        service = DataService('dummy.json')
        draws = service.load_draws()
        assert draws == []
    
    def test_save_draws(self, temp_json_file, sample_draw):
        """Test saving draws to file."""
        service = DataService(temp_json_file)
        draws = [sample_draw]
        
        result = service.save_draws(draws)
        assert result is True
        
        # Verify file content
        with open(temp_json_file, 'r') as f:
            data = json.load(f)
        assert len(data['draws']) == 1
        assert data['draws'][0]['id'] == '第650回'
    
    def test_save_draws_multiple(self, temp_json_file, multiple_draws_data):
        """Test saving multiple draws."""
        service = DataService(temp_json_file)
        draws = [Loto7Draw.from_dict(d) for d in multiple_draws_data['draws']]
        
        result = service.save_draws(draws)
        assert result is True
        
        with open(temp_json_file, 'r') as f:
            data = json.load(f)
        assert len(data['draws']) == 3
    
    @patch('builtins.open', side_effect=PermissionError)
    def test_save_draws_permission_error(self, mock_file, sample_draw):
        """Test save failure due to permission error."""
        service = DataService('dummy.json')
        result = service.save_draws([sample_draw])
        assert result is False
    
    def test_get_latest_draw(self, populated_data_file):
        """Test getting latest draw."""
        service = DataService(populated_data_file)
        latest = service.get_latest_draw()
        assert latest is not None
        assert latest.id == '第650回'
    
    def test_get_latest_draw_empty(self, temp_json_file):
        """Test getting latest draw from empty file."""
        with open(temp_json_file, 'w') as f:
            json.dump({'draws': []}, f)
        
        service = DataService(temp_json_file)
        latest = service.get_latest_draw()
        assert latest is None
    
    def test_get_draws_by_count(self, populated_data_file):
        """Test getting specific number of draws."""
        service = DataService(populated_data_file)
        draws = service.get_draws_by_count(2)
        assert len(draws) == 2
        assert draws[0].id == '第650回'
        assert draws[1].id == '第649回'
    
    def test_get_draws_by_count_exceeds_available(self, populated_data_file):
        """Test getting more draws than available."""
        service = DataService(populated_data_file)
        draws = service.get_draws_by_count(10)
        assert len(draws) == 3  # Only 3 available
    
    def test_parse_json_data_valid(self, multiple_draws_data):
        """Test parsing valid JSON data."""
        service = DataService('dummy.json')
        draws = service.parse_json_data(multiple_draws_data)
        assert len(draws) == 3
        assert all(isinstance(d, Loto7Draw) for d in draws)
    
    def test_parse_json_data_missing_draws_key(self):
        """Test parsing JSON without draws key."""
        service = DataService('dummy.json')
        with pytest.raises(ValueError, match='Invalid JSON format'):
            service.parse_json_data({'data': []})
    
    def test_parse_json_data_invalid_draw(self):
        """Test parsing JSON with invalid draw data."""
        service = DataService('dummy.json')
        invalid_data = {
            'draws': [{
                'id': '第650回',
                'date': '2024-10-31',
                'main': [1, 2, 3],  # Only 3 numbers (invalid)
                'bonus': [12, 21]
            }]
        }
        with pytest.raises(ValueError, match='Invalid draw data'):
            service.parse_json_data(invalid_data)
    
    def test_add_draw_success(self, temp_json_file, sample_draw):
        """Test adding new draw."""
        # Initialize with empty data
        with open(temp_json_file, 'w') as f:
            json.dump({'draws': []}, f)
        
        service = DataService(temp_json_file)
        result = service.add_draw(sample_draw)
        assert result is True
        
        draws = service.load_draws()
        assert len(draws) == 1
        assert draws[0].id == sample_draw.id
    
    def test_add_draw_duplicate_id(self, populated_data_file):
        """Test adding draw with duplicate ID."""
        service = DataService(populated_data_file)
        
        # Try to add draw with existing ID
        duplicate_draw = Loto7Draw(
            id='第650回',  # Already exists
            date='2024-11-01',
            main=[5, 10, 15, 20, 25, 30, 35],
            bonus=[1, 2]
        )
        
        with pytest.raises(ValueError, match='Duplicate draw ID'):
            service.add_draw(duplicate_draw)
    
    def test_add_draw_invalid_data(self, temp_json_file):
        """Test adding invalid draw."""
        with open(temp_json_file, 'w') as f:
            json.dump({'draws': []}, f)
        
        service = DataService(temp_json_file)
        
        invalid_draw = Loto7Draw(
            id='第651回',
            date='2024-11-01',
            main=[1, 2, 3],  # Invalid: only 3 numbers
            bonus=[5, 6]
        )
        
        with pytest.raises(ValueError, match='Invalid draw data'):
            service.add_draw(invalid_draw)
    
    def test_add_draw_inserts_at_beginning(self, populated_data_file):
        """Test that new draw is added at the beginning."""
        service = DataService(populated_data_file)
        
        new_draw = Loto7Draw(
            id='第651回',
            date='2024-11-05',
            main=[2, 9, 16, 23, 27, 31, 36],
            bonus=[5, 15]
        )
        
        service.add_draw(new_draw)
        draws = service.load_draws()
        
        assert draws[0].id == '第651回'
        assert len(draws) == 4
