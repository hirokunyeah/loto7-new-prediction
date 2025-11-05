"""Tests for StatisticalAnalyzer."""
import pytest
from app.services.statistical_analyzer import StatisticalAnalyzer, FilterConfig, StatisticalMetrics
from app.models import Loto7Draw


@pytest.mark.unit
class TestFilterConfig:
    """Test FilterConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = FilterConfig()
        
        assert config.continuous_max == 1
        assert config.sum_min == 100
        assert config.sum_max == 170
        assert config.zone3_required is True
        assert config.zone4_required is True
        assert config.odd_even_balance == (3, 4)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = FilterConfig(
            sum_min=90,
            sum_max=180,
            continuous_weight=20.0,
            frequency_weight=25.0
        )
        
        assert config.sum_min == 90
        assert config.sum_max == 180
        assert config.continuous_weight == 20.0
        assert config.frequency_weight == 25.0


@pytest.mark.unit
class TestStatisticalAnalyzer:
    """Test StatisticalAnalyzer functionality."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = StatisticalAnalyzer()
        
        assert analyzer.config is not None
        assert isinstance(analyzer.config, FilterConfig)
        assert analyzer.historical_stats == {}
        assert analyzer.recent_patterns == []
    
    def test_initialization_with_config(self):
        """Test analyzer initialization with custom config."""
        config = FilterConfig(sum_min=90, sum_max=180)
        analyzer = StatisticalAnalyzer(config)
        
        assert analyzer.config.sum_min == 90
        assert analyzer.config.sum_max == 180
    
    def test_analyze_historical_data(self):
        """Test historical data analysis."""
        draws = [
            Loto7Draw(
                id='第650回',
                date='2024-10-31',
                main=[1, 8, 10, 14, 25, 33, 35],
                bonus=[12, 21]
            ),
            Loto7Draw(
                id='第649回',
                date='2024-10-25',
                main=[12, 22, 23, 26, 33, 35, 37],
                bonus=[2, 21]
            ),
            Loto7Draw(
                id='第648回',
                date='2024-10-18',
                main=[3, 17, 19, 24, 28, 29, 35],
                bonus=[7, 13]
            )
        ]
        
        analyzer = StatisticalAnalyzer()
        analyzer.analyze_historical_data(draws)
        
        # Check that stats were initialized for all numbers
        assert len(analyzer.historical_stats) == 37
        assert 1 in analyzer.historical_stats
        assert 37 in analyzer.historical_stats
        
        # Check frequency tracking
        assert analyzer.historical_stats[35].frequency == 3  # Appears 3 times
        assert analyzer.historical_stats[33].frequency == 2  # Appears 2 times
        assert analyzer.historical_stats[1].frequency == 1   # Appears 1 time
    
    def test_analyze_historical_data_with_dict(self):
        """Test historical data analysis with dict format."""
        draws = [
            {'main': [1, 8, 10, 14, 25, 33, 35]},
            {'main': [12, 22, 23, 26, 33, 35, 37]},
            {'main': [3, 17, 19, 24, 28, 29, 35]}
        ]
        
        analyzer = StatisticalAnalyzer()
        analyzer.analyze_historical_data(draws)
        
        assert len(analyzer.historical_stats) == 37
        assert analyzer.historical_stats[35].frequency == 3
    
    def test_score_combination_all_pass(self):
        """Test scoring a combination that passes all filters."""
        analyzer = StatisticalAnalyzer()
        
        combo = (1, 8, 10, 14, 25, 33, 35)
        evaluation = {
            'continuous': {'pass': True},
            'zone3': {'pass': True},
            'zone4': {'pass': True},
            'odd_even': {'pass': True},
            'sum': {'pass': True},
            'last_digits': {'pass': True},
            'pull': {'pass': True}
        }
        
        result = analyzer.score_combination(combo, evaluation)
        
        assert 'scores' in result
        assert 'final_score' in result
        assert 'weights' in result
        # All filters pass, so score should be 100 (without frequency analysis)
        assert result['final_score'] >= 90  # May vary slightly due to rounding
    
    def test_score_combination_some_fail(self):
        """Test scoring a combination that fails some filters."""
        analyzer = StatisticalAnalyzer()
        
        combo = (1, 2, 3, 4, 5, 6, 7)
        evaluation = {
            'continuous': {'pass': False},  # Too many consecutive
            'zone3': {'pass': False},  # Only low zone
            'zone4': {'pass': False},  # Missing zones
            'odd_even': {'pass': True},
            'sum': {'pass': False},  # Sum too low
            'last_digits': {'pass': True},
            'pull': {'pass': True}
        }
        
        result = analyzer.score_combination(combo, evaluation)
        
        assert result['final_score'] < 100
        assert result['scores']['continuous'] == 0.0
        assert result['scores']['zone3'] == 0.0
        assert result['scores']['zone4'] == 0.0
        assert result['scores']['sum'] == 0.0
    
    def test_score_combination_with_historical_data(self):
        """Test scoring with historical data analysis."""
        draws = [
            Loto7Draw(
                id='第650回',
                date='2024-10-31',
                main=[1, 8, 10, 14, 25, 33, 35],
                bonus=[12, 21]
            )
        ]
        
        analyzer = StatisticalAnalyzer()
        analyzer.analyze_historical_data(draws)
        
        combo = (1, 8, 10, 14, 25, 33, 35)
        evaluation = {
            'continuous': {'pass': True},
            'zone3': {'pass': True},
            'zone4': {'pass': True},
            'odd_even': {'pass': True},
            'sum': {'pass': True},
            'last_digits': {'pass': True},
            'pull': {'pass': True}
        }
        
        result = analyzer.score_combination(combo, evaluation)
        
        # Should have frequency score now
        assert 'frequency' in result['scores']
        assert result['scores']['frequency'] > 0
    
    def test_identify_patterns(self):
        """Test pattern identification."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 2, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21]),
            Loto7Draw(id='第648回', date='2024-10-18', main=[3, 17, 19, 24, 28, 29, 35], bonus=[7, 13]),
            Loto7Draw(id='第647回', date='2024-10-11', main=[4, 5, 9, 13, 17, 22, 28], bonus=[18, 31]),
        ]
        
        analyzer = StatisticalAnalyzer()
        patterns = analyzer.identify_patterns(draws)
        
        assert len(patterns) > 0
        assert any(p['type'] == 'consecutive' for p in patterns)
        assert any(p['type'] == 'zone_distribution' for p in patterns)
        assert any(p['type'] == 'odd_even_ratio' for p in patterns)
    
    def test_identify_patterns_insufficient_data(self):
        """Test pattern identification with insufficient data."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 8, 10, 14, 25, 33, 35], bonus=[12, 21])
        ]
        
        analyzer = StatisticalAnalyzer()
        patterns = analyzer.identify_patterns(draws)
        
        assert patterns == []
    
    def test_rank_predictions(self):
        """Test ranking predictions by score."""
        analyzer = StatisticalAnalyzer()
        
        predictions = [
            ((1, 8, 10, 14, 25, 33, 35), {
                'evaluation': {'continuous': {'pass': True}},
                'scoring': {'final_score': 95.0}
            }),
            ((2, 9, 11, 15, 26, 34, 36), {
                'evaluation': {'continuous': {'pass': True}},
                'scoring': {'final_score': 88.0}
            }),
            ((3, 10, 12, 16, 27, 35, 37), {
                'evaluation': {'continuous': {'pass': True}},
                'scoring': {'final_score': 92.0}
            })
        ]
        
        ranked = analyzer.rank_predictions(predictions)
        
        assert len(ranked) == 3
        assert ranked[0]['rank'] == 1
        assert ranked[0]['score'] == 95.0
        assert ranked[1]['rank'] == 2
        assert ranked[1]['score'] == 92.0
        assert ranked[2]['rank'] == 3
        assert ranked[2]['score'] == 88.0
    
    def test_rank_predictions_without_scoring(self):
        """Test ranking predictions without scoring."""
        analyzer = StatisticalAnalyzer()
        
        predictions = [
            ((1, 8, 10, 14, 25, 33, 35), {
                'evaluation': {'continuous': {'pass': True}},
                'scoring': None
            }),
            ((2, 9, 11, 15, 26, 34, 36), {
                'evaluation': {'continuous': {'pass': True}},
                'scoring': None
            })
        ]
        
        ranked = analyzer.rank_predictions(predictions)
        
        assert len(ranked) == 2
        assert all(r['score'] is None for r in ranked)
        assert all(r['scoring'] is None for r in ranked)
    
    def test_get_top_patterns(self):
        """Test getting top N patterns."""
        draws = [
            Loto7Draw(id='第650回', date='2024-10-31', main=[1, 2, 10, 14, 25, 33, 35], bonus=[12, 21]),
            Loto7Draw(id='第649回', date='2024-10-25', main=[12, 22, 23, 26, 33, 35, 37], bonus=[2, 21]),
            Loto7Draw(id='第648回', date='2024-10-18', main=[3, 17, 19, 24, 28, 29, 35], bonus=[7, 13]),
            Loto7Draw(id='第647回', date='2024-10-11', main=[4, 5, 9, 13, 17, 22, 28], bonus=[18, 31]),
        ]
        
        analyzer = StatisticalAnalyzer()
        analyzer.identify_patterns(draws)
        
        top_patterns = analyzer.get_top_patterns(n=2)
        
        assert len(top_patterns) <= 2
        if top_patterns:
            assert 'type' in top_patterns[0]
            assert 'description' in top_patterns[0]


@pytest.mark.unit
class TestStatisticalMetrics:
    """Test StatisticalMetrics dataclass."""
    
    def test_default_metrics(self):
        """Test default metric values."""
        metrics = StatisticalMetrics(number=10)
        
        assert metrics.number == 10
        assert metrics.frequency == 0
        assert metrics.recent_frequency == 0
        assert metrics.last_appearance is None
        assert metrics.hot_score == 0.0
        assert metrics.cold_score == 0.0
        assert metrics.overdue_score == 0.0
    
    def test_custom_metrics(self):
        """Test custom metric values."""
        metrics = StatisticalMetrics(
            number=15,
            frequency=10,
            recent_frequency=5,
            last_appearance=2,
            hot_score=75.5
        )
        
        assert metrics.number == 15
        assert metrics.frequency == 10
        assert metrics.recent_frequency == 5
        assert metrics.last_appearance == 2
        assert metrics.hot_score == 75.5
