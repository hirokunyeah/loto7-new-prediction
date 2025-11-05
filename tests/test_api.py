"""Tests for API endpoints."""
import pytest
import json
from io import BytesIO


@pytest.mark.api
class TestDataEndpoint:
    """Test /api/data endpoint."""
    
    def test_get_data_empty(self, client):
        """Test getting data from empty database."""
        response = client.get('/api/data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['draws'] == []
        assert data['count'] == 0
    
    def test_get_data_with_draws(self, client, app, multiple_draws_data):
        """Test getting data with draws."""
        # Populate data
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.get('/api/data')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['count'] == 3
        assert len(data['draws']) == 3
    
    def test_get_data_with_evaluation(self, client, app, multiple_draws_data):
        """Test getting data with evaluation."""
        # Populate data
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.get('/api/data?evaluation=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['has_evaluation'] is True
        assert 'evaluation' in data['draws'][0]
        assert 'continuous' in data['draws'][0]['evaluation']
    
    def test_get_data_without_evaluation(self, client, app, multiple_draws_data):
        """Test getting data without evaluation."""
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.get('/api/data?evaluation=false')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['has_evaluation'] is False


@pytest.mark.api
class TestPredictEndpoint:
    """Test /api/predict endpoint."""
    
    def test_predict_basic(self, client):
        """Test basic prediction generation."""
        response = client.post('/api/predict',
                              json={'count': 5},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['draws']) == 5
        assert data['count'] == 5
    
    def test_predict_invalid_count_too_high(self, client):
        """Test prediction with count too high."""
        response = client.post('/api/predict',
                              json={'count': 150},
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_predict_invalid_count_too_low(self, client):
        """Test prediction with count too low."""
        response = client.post('/api/predict',
                              json={'count': 0},
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_predict_with_draw_number(self, client):
        """Test prediction with specific draw number."""
        response = client.post('/api/predict',
                              json={'count': 3, 'next_draw_number': 655},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['next_draw_number'] == 655
        assert '第655回' in data['draws'][0]['id']
        assert '候補1' in data['draws'][0]['id']
    
    def test_predict_auto_calculate_draw_number(self, client, app, multiple_draws_data):
        """Test prediction auto-calculates next draw number."""
        # Populate data with latest draw being 650
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.post('/api/predict',
                              json={'count': 2},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['next_draw_number'] == 651  # 650 + 1
    
    def test_predict_includes_evaluation(self, client):
        """Test that predictions include evaluation data."""
        response = client.post('/api/predict',
                              json={'count': 2},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'evaluation' in data['draws'][0]
        assert 'continuous' in data['draws'][0]['evaluation']


@pytest.mark.api
class TestUploadEndpoint:
    """Test /api/upload endpoint."""
    
    def test_upload_valid_file(self, client, multiple_draws_data):
        """Test uploading valid JSON file."""
        file_content = json.dumps(multiple_draws_data).encode('utf-8')
        data = {
            'file': (BytesIO(file_content), 'test.json')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200
        
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['count'] == 3
        assert len(response_data['draws']) == 3
    
    def test_upload_no_file(self, client):
        """Test upload without file."""
        response = client.post('/api/upload',
                              data={},
                              content_type='multipart/form-data')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_upload_invalid_extension(self, client):
        """Test upload with invalid file extension."""
        data = {
            'file': (BytesIO(b'test'), 'test.txt')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_upload_invalid_json(self, client):
        """Test upload with invalid JSON content."""
        file_content = b'invalid json content'
        data = {
            'file': (BytesIO(file_content), 'test.json')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_upload_invalid_draw_data(self, client):
        """Test upload with invalid draw data."""
        invalid_data = {
            'draws': [{
                'id': '第650回',
                'date': '2024-10-31',
                'main': [1, 2, 3],  # Only 3 numbers (invalid)
                'bonus': [12, 21]
            }]
        }
        file_content = json.dumps(invalid_data).encode('utf-8')
        data = {
            'file': (BytesIO(file_content), 'test.json')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400
        
        response_data = json.loads(response.data)
        assert response_data['success'] is False


@pytest.mark.api
class TestStatsEndpoint:
    """Test /api/stats endpoint."""
    
    def test_get_stats_empty(self, client):
        """Test getting statistics with no data."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_stats_with_data(self, client, app, multiple_draws_data):
        """Test getting statistics with data."""
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.get('/api/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'stats' in data
        assert data['stats']['total_draws'] == 3
        assert 'most_common_main' in data['stats']
        assert 'most_common_bonus' in data['stats']
        assert 'latest_draw' in data['stats']
    
    def test_get_stats_most_common_main(self, client, app, multiple_draws_data):
        """Test that most common main numbers are calculated correctly."""
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.get('/api/stats')
        data = json.loads(response.data)
        
        most_common = data['stats']['most_common_main']
        # 35 appears in all 3 draws
        assert [35, 3] in most_common
    
    def test_get_stats_latest_draw(self, client, app, multiple_draws_data):
        """Test that latest draw is returned correctly."""
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        response = client.get('/api/stats')
        data = json.loads(response.data)
        
        assert data['stats']['latest_draw']['id'] == '第650回'


@pytest.mark.api
class TestAddDrawEndpoint:
    """Test /api/add-draw endpoint."""
    
    def test_add_draw_success(self, client):
        """Test adding new draw."""
        new_draw = {
            'id': '第651回',
            'date': '2024-11-05',
            'main': [2, 9, 16, 23, 27, 31, 36],
            'bonus': [5, 15]
        }
        
        response = client.post('/api/add-draw',
                              json=new_draw,
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['draw']['id'] == '第651回'
    
    def test_add_draw_missing_field(self, client):
        """Test adding draw with missing field."""
        incomplete_draw = {
            'id': '第651回',
            'date': '2024-11-05',
            'main': [2, 9, 16, 23, 27, 31, 36]
            # Missing 'bonus'
        }
        
        response = client.post('/api/add-draw',
                              json=incomplete_draw,
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_add_draw_duplicate_id(self, client, app, multiple_draws_data):
        """Test adding draw with duplicate ID."""
        # Populate with existing data
        with open(app.config['LOTO7_DATA_FILE'], 'w') as f:
            json.dump(multiple_draws_data, f)
        
        duplicate_draw = {
            'id': '第650回',  # Already exists
            'date': '2024-11-05',
            'main': [2, 9, 16, 23, 27, 31, 36],
            'bonus': [5, 15]
        }
        
        response = client.post('/api/add-draw',
                              json=duplicate_draw,
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_add_draw_invalid_data(self, client):
        """Test adding draw with invalid data."""
        invalid_draw = {
            'id': '第651回',
            'date': '2024-11-05',
            'main': [1, 2, 3],  # Only 3 numbers (invalid)
            'bonus': [5, 15]
        }
        
        response = client.post('/api/add-draw',
                              json=invalid_draw,
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_add_draw_verifies_save(self, client, app):
        """Test that added draw is actually saved."""
        new_draw = {
            'id': '第651回',
            'date': '2024-11-05',
            'main': [2, 9, 16, 23, 27, 31, 36],
            'bonus': [5, 15]
        }
        
        response = client.post('/api/add-draw',
                              json=new_draw,
                              content_type='application/json')
        assert response.status_code == 200
        
        # Verify draw was saved by fetching data
        response = client.get('/api/data')
        data = json.loads(response.data)
        
        assert data['count'] == 1
        assert data['draws'][0]['id'] == '第651回'


@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API workflows."""
    
    def test_upload_then_predict_workflow(self, client, multiple_draws_data):
        """Test uploading data then generating predictions."""
        # Upload data
        file_content = json.dumps(multiple_draws_data).encode('utf-8')
        upload_data = {
            'file': (BytesIO(file_content), 'test.json')
        }
        
        upload_response = client.post('/api/upload',
                                     data=upload_data,
                                     content_type='multipart/form-data')
        assert upload_response.status_code == 200
        
        # Generate predictions (should use latest draw as reference)
        predict_response = client.post('/api/predict',
                                      json={'count': 3},
                                      content_type='application/json')
        assert predict_response.status_code == 200
        
        predict_data = json.loads(predict_response.data)
        assert predict_data['success'] is True
        assert len(predict_data['draws']) == 3
    
    def test_add_draw_then_get_stats_workflow(self, client):
        """Test adding draw then getting statistics."""
        # Add a draw
        new_draw = {
            'id': '第651回',
            'date': '2024-11-05',
            'main': [2, 9, 16, 23, 27, 31, 36],
            'bonus': [5, 15]
        }
        
        add_response = client.post('/api/add-draw',
                                  json=new_draw,
                                  content_type='application/json')
        assert add_response.status_code == 200
        
        # Get statistics
        stats_response = client.get('/api/stats')
        assert stats_response.status_code == 200
        
        stats_data = json.loads(stats_response.data)
        assert stats_data['stats']['total_draws'] == 1
        assert stats_data['stats']['latest_draw']['id'] == '第651回'
