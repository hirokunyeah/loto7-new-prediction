"""Tests for enhanced API endpoints with statistical analysis."""
import pytest
import json
from app.models import Loto7Draw


@pytest.mark.api
class TestEnhancedPredictEndpoint:
    """Test enhanced predict endpoint with scoring and patterns."""
    
    def test_predict_with_scoring_enabled(self, client, app):
        """Test prediction with scoring enabled (default)."""
        # Setup test data
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.post('/api/predict', json={
            'count': 5,
            'next_draw_number': 651,
            'include_scoring': True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['draws']) == 5
        
        # Check that evaluation includes scoring
        first_draw = data['draws'][0]
        assert 'evaluation' in first_draw
        if first_draw['evaluation']:
            assert 'scoring' in first_draw['evaluation']
            assert 'final_score' in first_draw['evaluation']['scoring']
            assert 0 <= first_draw['evaluation']['scoring']['final_score'] <= 100
    
    def test_predict_with_scoring_disabled(self, client, app):
        """Test prediction with scoring disabled."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.post('/api/predict', json={
            'count': 3,
            'include_scoring': False
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['draws']) == 3
    
    def test_predict_with_patterns(self, client, app):
        """Test prediction with pattern analysis."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21]),
            Loto7Draw(id='第648回', date='2024-10-18', main=[3, 17, 19, 24, 28, 29, 35], bonus=[7, 13]),
            Loto7Draw(id='第647回', date='2024-10-11', main=[4, 5, 9, 13, 17, 22, 28], bonus=[18, 31])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.post('/api/predict', json={
            'count': 5,
            'include_patterns': True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'patterns' in data
        assert isinstance(data['patterns'], list)
    
    def test_predict_with_custom_filter_config(self, client, app):
        """Test prediction with custom filter configuration."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.post('/api/predict', json={
            'count': 5,
            'filter_config': {
                'sum_min': 90,
                'sum_max': 180,
                'continuous_weight': 20.0,
                'frequency_weight': 25.0
            }
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_predict_with_insights(self, client, app):
        """Test prediction with statistical insights."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.post('/api/predict', json={
            'count': 5,
            'include_scoring': True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'insights' in data
        assert 'hot_numbers' in data['insights']
        assert 'cold_numbers' in data['insights']
        assert 'overdue_numbers' in data['insights']
    
    def test_predict_ranking_order(self, client, app):
        """Test that predictions are ranked by score."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.post('/api/predict', json={
            'count': 10,
            'include_scoring': True
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        
        # Extract scores
        scores = []
        for draw in data['draws']:
            if draw.get('evaluation') and draw['evaluation'].get('scoring'):
                scores.append(draw['evaluation']['scoring']['final_score'])
        
        # Check if scores are in descending order (ranked)
        if len(scores) > 1:
            assert scores == sorted(scores, reverse=True), "Predictions should be ranked by score"


@pytest.mark.api
class TestInsightsEndpoint:
    """Test the new /insights endpoint."""
    
    def test_get_insights_with_data(self, client, app):
        """Test getting insights with historical data."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21]),
            Loto7Draw(id='第648回', date='2024-10-18', main=[3, 17, 19, 24, 28, 29, 35], bonus=[7, 13]),
            Loto7Draw(id='第647回', date='2024-10-11', main=[4, 5, 9, 13, 17, 22, 28], bonus=[18, 31])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.get('/api/insights')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'insights' in data
        assert 'patterns' in data
        assert 'total_draws_analyzed' in data
        assert data['total_draws_analyzed'] == 4
        
        # Check insights structure
        insights = data['insights']
        assert 'hot_numbers' in insights
        assert 'cold_numbers' in insights
        assert 'overdue_numbers' in insights
        assert 'patterns' in insights
        
        # Check that lists contain proper data
        assert isinstance(insights['hot_numbers'], list)
        assert isinstance(insights['cold_numbers'], list)
        assert isinstance(insights['overdue_numbers'], list)
        
        if insights['hot_numbers']:
            assert 'number' in insights['hot_numbers'][0]
            assert 'score' in insights['hot_numbers'][0]
    
    def test_get_insights_empty_data(self, client, app):
        """Test getting insights with no data."""
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': []}, f)
        
        response = client.get('/api/insights')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_get_insights_patterns(self, client, app):
        """Test that insights include pattern analysis."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 2, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21]),
            Loto7Draw(id='第648回', date='2024-10-18', main=[3, 17, 19, 24, 28, 29, 35], bonus=[7, 13]),
            Loto7Draw(id='第647回', date='2024-10-11', main=[4, 5, 9, 13, 17, 22, 28], bonus=[18, 31])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.get('/api/insights')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'patterns' in data
        
        patterns = data['patterns']
        assert len(patterns) > 0
        
        # Check pattern structure
        for pattern in patterns:
            assert 'type' in pattern
            assert 'description' in pattern
            assert 'value' in pattern
    
    def test_get_insights_hot_numbers(self, client, app):
        """Test hot numbers calculation."""
        # Create data where certain numbers appear frequently in recent draws
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[1, 8, 22, 26, 33, 35, 37], bonus=[2, 21]),
            Loto7Draw(id='第648回', date='2024-10-18', main=[1, 8, 19, 24, 28, 33, 35], bonus=[7, 13])
        ]
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump({'draws': [d.to_dict() for d in draws]}, f)
        
        response = client.get('/api/insights')
        
        assert response.status_code == 200
        data = response.get_json()
        insights = data['insights']
        
        # Numbers 1, 8, 33, 35 appear in all 3 draws
        hot_numbers = insights['hot_numbers']
        hot_number_values = [item['number'] for item in hot_numbers]
        
        # Check that frequently appearing numbers are in hot list
        assert any(num in hot_number_values for num in [1, 8, 33, 35])
