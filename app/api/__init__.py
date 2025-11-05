"""API routes blueprint."""
from flask import Blueprint, request, jsonify, current_app
from app.services import DataService, PredictionService
from app.services.statistical_analyzer import FilterConfig
import json

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/data', methods=['GET'])
def get_data():
    """Get historical Loto7 draw data."""
    try:
        # Check if evaluation is requested
        include_evaluation = request.args.get('evaluation', 'false').lower() == 'true'
        
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        draws = data_service.load_draws()
        
        # Add evaluation to historical draws if requested
        if include_evaluation and draws:
            # Use the second-to-last draw as reference for the last draw's pull filter
            for i, draw in enumerate(draws):
                # Get previous draw for pull filter (if exists)
                previous_draw = draws[i + 1] if i + 1 < len(draws) else None
                prediction_service = PredictionService(previous_draw)
                
                # Evaluate the draw
                combo = tuple(sorted(draw.main))
                evaluation = prediction_service.evaluate_combination(combo)
                draw.evaluation = evaluation
        
        return jsonify({
            'success': True,
            'draws': [draw.to_dict() for draw in draws],
            'count': len(draws),
            'has_evaluation': include_evaluation
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'データの読み込みに失敗しました: {str(e)}'
        }), 500


@api.route('/predict', methods=['POST'])
def predict():
    """Generate predicted Loto7 numbers with enhanced statistical analysis."""
    try:
        data = request.get_json()
        num_predictions = data.get('count', 10)
        next_draw_number = data.get('next_draw_number', 650)
        include_scoring = data.get('include_scoring', True)
        include_patterns = data.get('include_patterns', False)
        
        # Get custom filter configuration if provided
        filter_config = None
        if 'filter_config' in data:
            config_data = data['filter_config']
            filter_config = FilterConfig(
                sum_min=config_data.get('sum_min', 100),
                sum_max=config_data.get('sum_max', 170),
                continuous_weight=config_data.get('continuous_weight', 10.0),
                zone3_weight=config_data.get('zone3_weight', 15.0),
                zone4_weight=config_data.get('zone4_weight', 15.0),
                odd_even_weight=config_data.get('odd_even_weight', 10.0),
                sum_weight=config_data.get('sum_weight', 15.0),
                last_digit_weight=config_data.get('last_digit_weight', 10.0),
                pull_weight=config_data.get('pull_weight', 10.0),
                frequency_weight=config_data.get('frequency_weight', 15.0)
            )
        
        # Validate input
        if not isinstance(num_predictions, int) or num_predictions < 1 or num_predictions > 100:
            return jsonify({
                'success': False,
                'message': '予測数は1から100の間で指定してください。'
            }), 400
        
        # Get the latest draw for the pull filter and determine next draw number
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        latest_draw = data_service.get_latest_draw()
        all_draws = data_service.load_draws()
        
        # Auto-calculate next draw number if not provided
        if latest_draw and next_draw_number == 650:
            # Extract number from draw ID (e.g., "第649回" -> 649)
            try:
                import re
                match = re.search(r'第(\d+)回', latest_draw.id)
                if match:
                    next_draw_number = int(match.group(1)) + 1
            except:
                pass
        
        # Generate predictions with enhanced statistical analysis
        prediction_service = PredictionService(
            previous_draw=latest_draw,
            config=filter_config,
            historical_draws=all_draws
        )
        
        # Identify patterns if requested
        if include_patterns and all_draws:
            patterns = prediction_service.analyzer.identify_patterns(all_draws)
        else:
            patterns = []
        
        predictions = prediction_service.generate_predictions(num_predictions)
        
        if not predictions:
            return jsonify({
                'success': False,
                'message': '予測の生成に失敗しました。フィルター条件が厳しすぎる可能性があります。'
            }), 400
        
        # Create draw objects with scoring
        predicted_draws = prediction_service.create_predicted_draws(
            predictions,
            next_draw_number,
            include_scoring=include_scoring
        )
        
        response_data = {
            'success': True,
            'draws': [draw.to_dict() for draw in predicted_draws],
            'count': len(predicted_draws),
            'next_draw_number': next_draw_number,
            'message': f'第{next_draw_number}回の予測候補を{len(predicted_draws)}件生成しました。'
        }
        
        # Add patterns if requested
        if include_patterns:
            response_data['patterns'] = patterns
        
        # Add statistical insights if scoring is enabled
        if include_scoring:
            response_data['insights'] = prediction_service.get_statistical_insights()
        
        return jsonify(response_data)
    
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


@api.route('/add-draw', methods=['POST'])
def add_draw():
    """Add a new lottery draw to the historical data."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'date', 'main', 'bonus']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'必須フィールド "{field}" が見つかりません。'
                }), 400
        
        # Create Loto7Draw object from the data
        from app.models import Loto7Draw
        try:
            new_draw = Loto7Draw.from_dict(data)
        except (KeyError, ValueError):
            return jsonify({
                'success': False,
                'message': 'データの形式が正しくありません。'
            }), 400
        
        # Add the new draw using DataService
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        try:
            success = data_service.add_draw(new_draw)
            if success:
                return jsonify({
                    'success': True,
                    'draw': new_draw.to_dict(),
                    'message': f'{new_draw.id} のデータを追加しました。'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'データの保存に失敗しました。'
                }), 500
        except ValueError as e:
            # Map controlled error messages to user-friendly Japanese messages
            error_msg = str(e)
            if error_msg == 'Duplicate draw ID':
                user_message = 'この回数は既に登録されています。'
            elif error_msg == 'Invalid draw data':
                user_message = '抽選データが無効です。番号が正しいか確認してください。'
            else:
                user_message = 'データの検証に失敗しました。'
            
            return jsonify({
                'success': False,
                'message': user_message
            }), 400
    
    except Exception:
        return jsonify({
            'success': False,
            'message': 'データの追加に失敗しました。'
        }), 500


@api.route('/insights', methods=['GET'])
def get_insights():
    """Get statistical insights from historical data."""
    try:
        data_service = DataService(current_app.config['LOTO7_DATA_FILE'])
        all_draws = data_service.load_draws()
        
        if not all_draws:
            return jsonify({
                'success': True,
                'insights': {},
                'message': 'データがありません。'
            })
        
        # Create prediction service with historical data
        latest_draw = all_draws[0] if all_draws else None
        prediction_service = PredictionService(
            previous_draw=latest_draw,
            historical_draws=all_draws
        )
        
        # Identify patterns
        patterns = prediction_service.analyzer.identify_patterns(all_draws)
        
        # Get statistical insights
        insights = prediction_service.get_statistical_insights()
        
        return jsonify({
            'success': True,
            'insights': insights,
            'patterns': patterns,
            'total_draws_analyzed': len(all_draws)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'統計分析に失敗しました: {str(e)}'
        }), 500
