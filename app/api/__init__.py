"""API routes blueprint."""
from flask import Blueprint, request, jsonify, current_app
from app.services import DataService, PredictionService
import json

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/data', methods=['GET'])
def get_data():
    """Get historical Loto7 draw data."""
    try:
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        draws = data_service.load_draws()
        
        return jsonify({
            'success': True,
            'draws': [draw.to_dict() for draw in draws],
            'count': len(draws)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'データの読み込みに失敗しました: {str(e)}'
        }), 500


@api.route('/predict', methods=['POST'])
def predict():
    """Generate predicted Loto7 numbers."""
    try:
        data = request.get_json()
        num_predictions = data.get('count', 10)
        start_draw_number = data.get('start_draw_number', 650)
        
        # Validate input
        if not isinstance(num_predictions, int) or num_predictions < 1 or num_predictions > 100:
            return jsonify({
                'success': False,
                'message': '予測数は1から100の間で指定してください。'
            }), 400
        
        # Get the latest draw for the pull filter
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        latest_draw = data_service.get_latest_draw()
        
        # Generate predictions
        prediction_service = PredictionService(latest_draw)
        predictions = prediction_service.generate_predictions(num_predictions)
        
        if not predictions:
            return jsonify({
                'success': False,
                'message': '予測の生成に失敗しました。フィルター条件が厳しすぎる可能性があります。'
            }), 400
        
        # Create draw objects
        predicted_draws = prediction_service.create_predicted_draws(
            predictions,
            start_draw_number
        )
        
        return jsonify({
            'success': True,
            'draws': [draw.to_dict() for draw in predicted_draws],
            'count': len(predicted_draws),
            'message': f'{len(predicted_draws)}件の予測を生成しました。'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'予測の生成に失敗しました: {str(e)}'
        }), 500


@api.route('/upload', methods=['POST'])
def upload():
    """Upload and parse Loto7 data from JSON file."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'ファイルが選択されていません。'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'ファイルが選択されていません。'
            }), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({
                'success': False,
                'message': '.jsonファイルを選択してください。'
            }), 400
        
        # Parse JSON
        try:
            json_data = json.loads(file.read().decode('utf-8'))
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'message': 'JSONファイルの形式が正しくありません。'
            }), 400
        
        # Validate and parse draws
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        try:
            draws = data_service.parse_json_data(json_data)
        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        
        return jsonify({
            'success': True,
            'draws': [draw.to_dict() for draw in draws],
            'count': len(draws),
            'message': f'{len(draws)}件のデータを読み込みました。'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'ファイルのアップロードに失敗しました: {str(e)}'
        }), 500


@api.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about historical draws."""
    try:
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        draws = data_service.load_draws()
        
        if not draws:
            return jsonify({
                'success': True,
                'stats': {},
                'message': 'データがありません。'
            })
        
        # Calculate statistics
        all_main_numbers = []
        all_bonus_numbers = []
        
        for draw in draws:
            all_main_numbers.extend(draw.main)
            all_bonus_numbers.extend(draw.bonus)
        
        from collections import Counter
        main_counter = Counter(all_main_numbers)
        bonus_counter = Counter(all_bonus_numbers)
        
        stats = {
            'total_draws': len(draws),
            'most_common_main': main_counter.most_common(10),
            'most_common_bonus': bonus_counter.most_common(10),
            'latest_draw': draws[0].to_dict() if draws else None
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'統計の取得に失敗しました: {str(e)}'
        }), 500
