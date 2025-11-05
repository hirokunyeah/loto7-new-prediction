"""Tests for PredictionService - Focus on 7 filters."""
import pytest
from app.services.prediction_service import PredictionService
from app.models import Loto7Draw


@pytest.mark.unit
class TestPredictionServiceFilters:
    """Test the 7 prediction filters."""
    
    def test_has_continuous_no_consecutive(self):
        """Test continuous filter: no consecutive numbers."""
        service = PredictionService()
        combo = (1, 5, 10, 15, 20, 25, 30)
        assert service._has_continuous(combo) is False
    
    def test_has_continuous_with_consecutive(self):
        """Test continuous filter: has consecutive numbers."""
        service = PredictionService()
        combo = (1, 2, 10, 15, 20, 25, 30)
        assert service._has_continuous(combo) is True
    
    def test_has_continuous_multiple_consecutive(self):
        """Test continuous filter: multiple consecutive numbers."""
        service = PredictionService()
        combo = (1, 2, 3, 15, 20, 25, 30)
        assert service._has_continuous(combo) is True
    
    def test_check_zone3_all_zones_covered(self):
        """Test zone3 filter: all 3 zones covered."""
        service = PredictionService()
        combo = (2, 8, 15, 20, 27, 30, 35)  # low, mid, high
        assert service._check_zone3(combo) is True
    
    def test_check_zone3_missing_zone(self):
        """Test zone3 filter: missing a zone."""
        service = PredictionService()
        combo = (1, 2, 3, 4, 5, 6, 7)  # Only low zone
        assert service._check_zone3(combo) is False
    
    def test_check_zone3_only_high_zone(self):
        """Test zone3 filter: only high zone."""
        service = PredictionService()
        combo = (26, 27, 28, 29, 30, 31, 32)
        assert service._check_zone3(combo) is False
    
    def test_check_zone4_all_zones_covered(self):
        """Test zone4 filter: all 4 zones covered."""
        service = PredictionService()
        combo = (1, 12, 20, 30, 5, 15, 35)
        assert service._check_zone4(combo) is True
    
    def test_check_zone4_missing_zone(self):
        """Test zone4 filter: missing a zone."""
        service = PredictionService()
        combo = (1, 2, 3, 10, 11, 12, 15)  # Missing C and D zones
        assert service._check_zone4(combo) is False
    
    def test_check_odd_even_balanced_3_4(self):
        """Test odd/even filter: 3 odd, 4 even."""
        service = PredictionService()
        combo = (1, 3, 5, 2, 4, 6, 8)  # 3 odd, 4 even
        assert service._check_odd_even(combo) is True
    
    def test_check_odd_even_balanced_4_3(self):
        """Test odd/even filter: 4 odd, 3 even."""
        service = PredictionService()
        combo = (1, 3, 5, 7, 2, 4, 6)  # 4 odd, 3 even
        assert service._check_odd_even(combo) is True
    
    def test_check_odd_even_unbalanced_all_odd(self):
        """Test odd/even filter: all odd (unbalanced)."""
        service = PredictionService()
        combo = (1, 3, 5, 7, 9, 11, 13)  # 7 odd, 0 even
        assert service._check_odd_even(combo) is False
    
    def test_check_odd_even_unbalanced_5_2(self):
        """Test odd/even filter: 5 odd, 2 even (unbalanced)."""
        service = PredictionService()
        combo = (1, 3, 5, 7, 9, 2, 4)  # 5 odd, 2 even
        assert service._check_odd_even(combo) is False
    
    def test_check_sum_in_range(self):
        """Test sum filter: sum within range."""
        service = PredictionService()
        combo = (10, 15, 18, 19, 20, 21, 23)  # Sum = 126
        assert service._check_sum(combo) is True
    
    def test_check_sum_below_range(self):
        """Test sum filter: sum below range."""
        service = PredictionService()
        combo = (1, 2, 3, 4, 5, 6, 7)  # Sum = 28
        assert service._check_sum(combo) is False
    
    def test_check_sum_above_range(self):
        """Test sum filter: sum above range."""
        service = PredictionService()
        combo = (31, 32, 33, 34, 35, 36, 37)  # Sum = 238
        assert service._check_sum(combo) is False
    
    def test_check_sum_at_minimum_boundary(self):
        """Test sum filter: at minimum boundary (100)."""
        service = PredictionService()
        combo = (1, 2, 3, 4, 5, 6, 79)  # Sum = 100
        # Note: 79 is out of range, so this is just for sum testing logic
        # In practice, valid combos would be like (1, 2, 8, 10, 15, 28, 36) = 100
        combo_valid = (1, 2, 8, 10, 15, 28, 36)  # Sum = 100
        assert service._check_sum(combo_valid) is True
    
    def test_check_sum_at_maximum_boundary(self):
        """Test sum filter: at maximum boundary (170)."""
        service = PredictionService()
        combo = (15, 20, 22, 25, 27, 30, 31)  # Sum = 170
        assert service._check_sum(combo) is True
    
    def test_check_last_digits_valid_distribution(self):
        """Test last digits filter: valid distribution."""
        service = PredictionService()
        combo = (1, 12, 23, 34, 5, 16, 27)  # Last digits: 1,2,3,4,5,6,7 (max 1 each)
        assert service._check_last_digits(combo) is True
    
    def test_check_last_digits_max_2_duplicates(self):
        """Test last digits filter: 2 duplicates (valid)."""
        service = PredictionService()
        combo = (1, 11, 23, 24, 5, 16, 27)  # Last digits: 1,1,3,4,5,6,7 (max 2)
        assert service._check_last_digits(combo) is True
    
    def test_check_last_digits_too_many_duplicates(self):
        """Test last digits filter: 3+ duplicates (invalid)."""
        service = PredictionService()
        combo = (1, 11, 21, 31, 5, 15, 25)  # Last digits: 1,1,1,1,5,5,5 (max 4)
        assert service._check_last_digits(combo) is False
    
    def test_check_pull_no_previous_draw(self):
        """Test pull filter: no previous draw set."""
        service = PredictionService()
        combo = (1, 8, 10, 14, 25, 33, 35)
        assert service._check_pull(combo) is True
    
    def test_check_pull_no_overlap(self):
        """Test pull filter: no overlap with previous draw."""
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        service = PredictionService(previous)
        combo = (1, 5, 8, 10, 14, 15, 19)  # No overlap
        assert service._check_pull(combo) is True
    
    def test_check_pull_one_overlap(self):
        """Test pull filter: 1 overlap (valid)."""
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        service = PredictionService(previous)
        combo = (12, 5, 8, 10, 14, 15, 19)  # 1 overlap (12)
        assert service._check_pull(combo) is True
    
    def test_check_pull_two_overlaps(self):
        """Test pull filter: 2+ overlaps (invalid)."""
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        service = PredictionService(previous)
        combo = (12, 22, 8, 10, 14, 15, 19)  # 2 overlaps (12, 22)
        assert service._check_pull(combo) is False
    
    def test_check_pull_includes_bonus_numbers(self):
        """Test pull filter: includes previous bonus numbers."""
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        service = PredictionService(previous)
        combo = (2, 5, 8, 10, 14, 15, 19)  # 1 overlap with bonus (2)
        assert service._check_pull(combo) is True


@pytest.mark.unit
class TestPredictionServiceEvaluation:
    """Test combination evaluation."""
    
    def test_evaluate_combination_structure(self):
        """Test evaluation returns correct structure."""
        service = PredictionService()
        combo = (1, 8, 10, 14, 25, 33, 35)
        
        evaluation = service.evaluate_combination(combo)
        
        assert 'continuous' in evaluation
        assert 'zone3' in evaluation
        assert 'zone4' in evaluation
        assert 'odd_even' in evaluation
        assert 'sum' in evaluation
        assert 'last_digits' in evaluation
        assert 'pull' in evaluation
        assert 'overall_pass' in evaluation
    
    def test_evaluate_combination_pass_flags(self):
        """Test evaluation includes pass flags."""
        service = PredictionService()
        combo = (1, 8, 10, 14, 25, 33, 35)
        
        evaluation = service.evaluate_combination(combo)
        
        assert 'pass' in evaluation['continuous']
        assert 'pass' in evaluation['zone3']
        assert 'pass' in evaluation['zone4']
        assert 'pass' in evaluation['odd_even']
        assert 'pass' in evaluation['sum']
        assert 'pass' in evaluation['last_digits']
        assert 'pass' in evaluation['pull']
    
    def test_evaluate_combination_with_previous_draw(self):
        """Test evaluation with previous draw set."""
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        service = PredictionService(previous)
        combo = (1, 8, 10, 14, 25, 33, 36)
        
        evaluation = service.evaluate_combination(combo)
        
        assert evaluation['pull']['count'] == 1  # 33 overlaps
    
    def test_evaluate_combination_details(self):
        """Test evaluation contains detailed information."""
        service = PredictionService()
        combo = (1, 8, 10, 14, 25, 33, 35)
        
        evaluation = service.evaluate_combination(combo)
        
        # Check zone3 details
        assert 'distribution' in evaluation['zone3']
        
        # Check odd_even details
        assert 'odd' in evaluation['odd_even']
        assert 'even' in evaluation['odd_even']
        
        # Check sum details
        assert 'total' in evaluation['sum']
        assert evaluation['sum']['total'] == sum(combo)


@pytest.mark.unit
class TestPredictionServiceGeneration:
    """Test prediction generation."""
    
    def test_generate_predictions_returns_tuples(self):
        """Test that generation returns tuple combinations."""
        service = PredictionService()
        predictions = service.generate_predictions(count=5)
        
        assert len(predictions) <= 5
        assert all(isinstance(p, tuple) for p in predictions)
        assert all(len(p) == 7 for p in predictions)
    
    def test_generate_predictions_unique(self):
        """Test that predictions are unique."""
        service = PredictionService()
        predictions = service.generate_predictions(count=10)
        
        assert len(predictions) == len(set(predictions))
    
    def test_generate_predictions_all_pass_filters(self):
        """Test that all generated predictions pass filters."""
        service = PredictionService()
        predictions = service.generate_predictions(count=5)
        
        for pred in predictions:
            assert service._apply_filters(pred) is True
    
    def test_generate_predictions_with_previous_draw(self):
        """Test prediction generation with previous draw."""
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        service = PredictionService(previous)
        predictions = service.generate_predictions(count=5)
        
        # All predictions should pass pull filter
        for pred in predictions:
            assert service._check_pull(pred) is True
    
    def test_generate_bonus_numbers(self):
        """Test bonus number generation."""
        service = PredictionService()
        main = [1, 8, 10, 14, 25, 33, 35]
        bonus = service.generate_bonus_numbers(main)
        
        assert len(bonus) == 2
        assert all(1 <= n <= 37 for n in bonus)
        assert len(set(bonus)) == 2
        assert not any(n in main for n in bonus)
        assert bonus == sorted(bonus)  # Should be sorted
    
    def test_generate_bonus_numbers_no_overlap(self):
        """Test bonus numbers don't overlap with main."""
        service = PredictionService()
        main = [1, 2, 3, 4, 5, 6, 7]
        bonus = service.generate_bonus_numbers(main)
        
        assert all(n not in main for n in bonus)
    
    def test_create_predicted_draws(self):
        """Test creating Loto7Draw objects from predictions."""
        service = PredictionService()
        predictions = [(1, 8, 10, 14, 25, 33, 35), (2, 9, 11, 15, 26, 34, 36)]
        
        draws = service.create_predicted_draws(predictions, next_draw_number=651)
        
        assert len(draws) == 2
        assert draws[0].id == '第651回 候補1'
        assert draws[1].id == '第651回 候補2'
        assert all(isinstance(d, Loto7Draw) for d in draws)
        assert all(len(d.bonus) == 2 for d in draws)
    
    def test_create_predicted_draws_with_evaluation(self):
        """Test creating predicted draws with evaluation."""
        service = PredictionService()
        predictions = [(1, 8, 10, 14, 25, 33, 35)]
        
        draws = service.create_predicted_draws(
            predictions,
            next_draw_number=651,
            include_evaluation=True
        )
        
        assert draws[0].evaluation is not None
        assert 'continuous' in draws[0].evaluation
        assert 'zone3' in draws[0].evaluation
        assert 'overall_pass' in draws[0].evaluation
    
    def test_create_predicted_draws_without_evaluation(self):
        """Test creating predicted draws without evaluation."""
        service = PredictionService()
        predictions = [(1, 8, 10, 14, 25, 33, 35)]
        
        draws = service.create_predicted_draws(
            predictions,
            next_draw_number=651,
            include_evaluation=False
        )
        
        assert draws[0].evaluation is None
    
    def test_set_previous_draw(self):
        """Test setting previous draw after initialization."""
        service = PredictionService()
        
        previous = Loto7Draw(
            id='第649回',
            date='2024-10-25',
            main=[12, 22, 23, 26, 33, 35, 37],
            bonus=[2, 21]
        )
        
        service.set_previous_draw(previous)
        
        assert len(service.previous_draw_numbers) == 9  # 7 main + 2 bonus
        assert 12 in service.previous_draw_numbers
        assert 2 in service.previous_draw_numbers
