"""Tests for Loto7Draw model."""
import pytest
from app.models import Loto7Draw


@pytest.mark.unit
class TestLoto7Draw:
    """Test Loto7Draw data model."""
    
    def test_create_draw_from_dict(self, sample_draw_data):
        """Test creating draw from dictionary."""
        draw = Loto7Draw.from_dict(sample_draw_data)
        assert draw.id == '第650回'
        assert draw.date == '2024-10-31'
        assert draw.main == [1, 8, 10, 14, 25, 33, 35]
        assert draw.bonus == [12, 21]
    
    def test_create_draw_with_string_numbers(self):
        """Test creating draw with string-formatted numbers."""
        data = {
            'id': '第650回',
            'date': '2024-10-31',
            'main': ['01', '08', '10', '14', '25', '33', '35'],
            'bonus': ['12', '21']
        }
        draw = Loto7Draw.from_dict(data)
        assert draw.main == [1, 8, 10, 14, 25, 33, 35]
        assert draw.bonus == [12, 21]
    
    def test_to_dict(self, sample_draw):
        """Test converting draw to dictionary."""
        data = sample_draw.to_dict()
        assert data['id'] == '第650回'
        assert data['date'] == '2024-10-31'
        assert data['main'] == [1, 8, 10, 14, 25, 33, 35]
        assert data['bonus'] == [12, 21]
        assert 'evaluation' not in data
    
    def test_to_dict_with_evaluation(self, sample_draw):
        """Test converting draw with evaluation to dictionary."""
        sample_draw.evaluation = {'test': 'data'}
        data = sample_draw.to_dict()
        assert 'evaluation' in data
        assert data['evaluation'] == {'test': 'data'}
    
    def test_validate_valid_draw(self, sample_draw):
        """Test validation of valid draw."""
        assert sample_draw.validate() is True
    
    def test_validate_invalid_main_count(self):
        """Test validation fails with wrong main number count."""
        draw = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[1, 8, 10, 14, 25, 33],  # Only 6 numbers
            bonus=[12, 21]
        )
        assert draw.validate() is False
    
    def test_validate_invalid_bonus_count(self):
        """Test validation fails with wrong bonus number count."""
        draw = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[1, 8, 10, 14, 25, 33, 35],
            bonus=[12]  # Only 1 number
        )
        assert draw.validate() is False
    
    def test_validate_out_of_range_main(self):
        """Test validation fails with out-of-range main number."""
        draw = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[0, 8, 10, 14, 25, 33, 35],  # 0 is out of range
            bonus=[12, 21]
        )
        assert draw.validate() is False
        
        draw2 = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[1, 8, 10, 14, 25, 33, 38],  # 38 is out of range
            bonus=[12, 21]
        )
        assert draw2.validate() is False
    
    def test_validate_duplicate_main_numbers(self):
        """Test validation fails with duplicate main numbers."""
        draw = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[1, 8, 10, 10, 25, 33, 35],  # 10 appears twice
            bonus=[12, 21]
        )
        assert draw.validate() is False
    
    def test_validate_duplicate_bonus_numbers(self):
        """Test validation fails with duplicate bonus numbers."""
        draw = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[1, 8, 10, 14, 25, 33, 35],
            bonus=[12, 12]  # 12 appears twice
        )
        assert draw.validate() is False
    
    def test_validate_overlap_main_bonus(self):
        """Test validation fails with overlap between main and bonus."""
        draw = Loto7Draw(
            id='第650回',
            date='2024-10-31',
            main=[1, 8, 10, 14, 25, 33, 35],
            bonus=[8, 21]  # 8 is in main numbers
        )
        assert draw.validate() is False
