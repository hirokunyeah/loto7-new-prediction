"""Service for generating Loto7 number predictions."""
import random
from typing import List, Set, Tuple, Optional, Dict, Any
from collections import Counter
from datetime import datetime, timedelta
from app.models import Loto7Draw
from app.services.statistical_analyzer import StatisticalAnalyzer, FilterConfig


class PredictionService:
    """Handles Loto7 number prediction logic."""
    
    def __init__(
        self, 
        previous_draw: Optional[Loto7Draw] = None,
        config: Optional[FilterConfig] = None,
        historical_draws: Optional[List[Loto7Draw]] = None
    ):
        """Initialize prediction service."""
        self.previous_draw_numbers = set()
        if previous_draw:
            self.previous_draw_numbers = set(previous_draw.main + previous_draw.bonus)
        
        # Initialize statistical analyzer
        self.analyzer = StatisticalAnalyzer(config)
        
        # Analyze historical data if provided
        if historical_draws:
            self.analyzer.analyze_historical_data(historical_draws)
        
        # Filter settings (use config if provided, otherwise use defaults)
        self.config = config or FilterConfig()
        self.sum_min = self.config.sum_min
        self.sum_max = self.config.sum_max
    
    def set_previous_draw(self, draw: Loto7Draw):
        """Set the previous draw for pull filter."""
        self.previous_draw_numbers = set(draw.main + draw.bonus)
    
    def _has_continuous(self, combo: Tuple[int, ...]) -> bool:
        """Check if numbers have consecutive digits."""
        for i in range(len(combo) - 1):
            if combo[i] + 1 == combo[i + 1]:
                return True
        return False
    
    def _check_zone3(self, combo: Tuple[int, ...]) -> bool:
        """Check if numbers are distributed across 3 zones."""
        low = any(1 <= n <= 12 for n in combo)
        mid = any(13 <= n <= 25 for n in combo)
        high = any(26 <= n <= 37 for n in combo)
        return low and mid and high
    
    def _check_zone4(self, combo: Tuple[int, ...]) -> bool:
        """Check if numbers are distributed across 4 zones."""
        a = any(1 <= n <= 9 for n in combo)
        b = any(10 <= n <= 18 for n in combo)
        c = any(19 <= n <= 27 for n in combo)
        d = any(28 <= n <= 37 for n in combo)
        return a and b and c and d
    
    def _check_odd_even(self, combo: Tuple[int, ...]) -> bool:
        """Check odd/even number balance."""
        odd_count = sum(1 for n in combo if n % 2 != 0)
        return odd_count in [3, 4]
    
    def _check_sum(self, combo: Tuple[int, ...]) -> bool:
        """Check if sum is within range."""
        total = sum(combo)
        return self.sum_min <= total <= self.sum_max
    
    def _check_last_digits(self, combo: Tuple[int, ...]) -> bool:
        """Check distribution of last digits."""
        last_digits = [n % 10 for n in combo]
        counts = Counter(last_digits)
        return max(counts.values()) < 3
    
    def _check_pull(self, combo: Tuple[int, ...]) -> bool:
        """Check overlap with previous draw."""
        if not self.previous_draw_numbers:
            return True
        combo_set = set(combo)
        pull_count = len(combo_set.intersection(self.previous_draw_numbers))
        return pull_count in [0, 1]
    
    def _apply_filters(self, combo: Tuple[int, ...]) -> bool:
        """Apply all filters to a combination."""
        filters = [
            self._has_continuous,
            self._check_zone3,
            self._check_zone4,
            self._check_odd_even,
            self._check_sum,
            self._check_last_digits,
            self._check_pull
        ]
        return all(flt(combo) for flt in filters)
    
    def evaluate_combination(self, combo: Tuple[int, ...]) -> dict:
        """Evaluate a combination and return detailed filter results."""
        odd_count = sum(1 for n in combo if n % 2 != 0)
        even_count = 7 - odd_count
        total = sum(combo)
        last_digits = [n % 10 for n in combo]
        last_digit_counts = Counter(last_digits)
        
        # Zone distribution
        zone3 = {
            'low (1-12)': sum(1 for n in combo if 1 <= n <= 12),
            'mid (13-25)': sum(1 for n in combo if 13 <= n <= 25),
            'high (26-37)': sum(1 for n in combo if 26 <= n <= 37)
        }
        
        zone4 = {
            'A (1-9)': sum(1 for n in combo if 1 <= n <= 9),
            'B (10-18)': sum(1 for n in combo if 10 <= n <= 18),
            'C (19-27)': sum(1 for n in combo if 19 <= n <= 27),
            'D (28-37)': sum(1 for n in combo if 28 <= n <= 37)
        }
        
        # Pull count
        pull_count = 0
        if self.previous_draw_numbers:
            pull_count = len(set(combo).intersection(self.previous_draw_numbers))
        
        # Consecutive numbers
        consecutive_pairs = []
        for i in range(len(combo) - 1):
            if combo[i] + 1 == combo[i + 1]:
                consecutive_pairs.append(f"{combo[i]}-{combo[i+1]}")
        
        return {
            'continuous': {
                'has_continuous': self._has_continuous(combo),
                'pairs': consecutive_pairs,
                'pass': self._has_continuous(combo)
            },
            'zone3': {
                'distribution': zone3,
                'all_zones_covered': self._check_zone3(combo),
                'pass': self._check_zone3(combo)
            },
            'zone4': {
                'distribution': zone4,
                'all_zones_covered': self._check_zone4(combo),
                'pass': self._check_zone4(combo)
            },
            'odd_even': {
                'odd': odd_count,
                'even': even_count,
                'balance': f"{odd_count}:{even_count}",
                'pass': self._check_odd_even(combo)
            },
            'sum': {
                'total': total,
                'range': f"{self.sum_min}-{self.sum_max}",
                'in_range': self.sum_min <= total <= self.sum_max,
                'pass': self._check_sum(combo)
            },
            'last_digits': {
                'distribution': dict(last_digit_counts),
                'max_count': max(last_digit_counts.values()),
                'pass': self._check_last_digits(combo)
            },
            'pull': {
                'count': pull_count,
                'valid_range': '0-1',
                'pass': self._check_pull(combo)
            },
            'overall_pass': self._apply_filters(combo)
        }
    
    def generate_bonus_numbers(self, main_numbers: List[int]) -> List[int]:
        """Generate bonus numbers that don't overlap with main numbers."""
        available_numbers = [n for n in range(1, 38) if n not in main_numbers]
        return sorted(random.sample(available_numbers, 2))
    
    def generate_predictions(self, count: int = 10, max_attempts: int = 1_000_000) -> List[Tuple[int]]:
        """Generate predicted number combinations."""
        candidates = set()
        all_numbers = list(range(1, 38))
        attempts = 0
        
        while len(candidates) < count and attempts < max_attempts:
            attempts += 1
            combo = tuple(sorted(random.sample(all_numbers, 7)))
            
            if self._apply_filters(combo):
                candidates.add(combo)
        
        return list(candidates)
    
    def create_predicted_draws(
        self,
        predictions: List[Tuple[int]],
        next_draw_number: int = 650,
        include_evaluation: bool = True,
        include_scoring: bool = True
    ) -> List[Loto7Draw]:
        """Create Loto7Draw objects from predictions with scoring.
        All predictions are for the same draw number (next draw).
        """
        draws = []
        predictions_with_scores = []
        next_draw_date = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d")
        
        for combo in predictions:
            # Generate evaluation data
            evaluation = None
            if include_evaluation:
                evaluation = self.evaluate_combination(combo)
            
            # Calculate score if requested
            scoring = None
            if include_scoring and evaluation:
                scoring = self.analyzer.score_combination(
                    combo,
                    evaluation,
                    self.previous_draw_numbers
                )
            
            predictions_with_scores.append((combo, {
                'evaluation': evaluation,
                'scoring': scoring
            }))
        
        # Rank predictions by score if scoring is enabled
        if include_scoring:
            ranked_predictions = self.analyzer.rank_predictions(predictions_with_scores)
            
            for item in ranked_predictions:
                combo = tuple(item['combination'])
                rank = item['rank']
                score = item['score']
                
                draw_id = f"第{next_draw_number}回 候補{rank}"
                bonus_numbers = self.generate_bonus_numbers(list(combo))
                
                # Add scoring info to evaluation
                evaluation = item['evaluation']
                if evaluation and item['scoring']:
                    evaluation['scoring'] = item['scoring']
                
                draw = Loto7Draw(
                    id=draw_id,
                    date=next_draw_date,
                    main=list(combo),
                    bonus=bonus_numbers,
                    evaluation=evaluation
                )
                draws.append(draw)
        else:
            # Original behavior without ranking
            for i, (combo, data) in enumerate(predictions_with_scores):
                draw_id = f"第{next_draw_number}回 候補{i + 1}"
                bonus_numbers = self.generate_bonus_numbers(list(combo))
                
                draw = Loto7Draw(
                    id=draw_id,
                    date=next_draw_date,
                    main=list(combo),
                    bonus=bonus_numbers,
                    evaluation=data['evaluation']
                )
                draws.append(draw)
        
        return draws
    
    def get_statistical_insights(self) -> Dict[str, Any]:
        """Get statistical insights from historical data analysis."""
        if not self.analyzer.historical_stats:
            return {
                'message': 'No historical data analyzed yet',
                'stats': {}
            }
        
        # Get top hot, cold, and overdue numbers
        stats = list(self.analyzer.historical_stats.values())
        hot_numbers = sorted(stats, key=lambda x: x.hot_score, reverse=True)[:10]
        cold_numbers = sorted(stats, key=lambda x: x.cold_score, reverse=True)[:10]
        overdue_numbers = sorted(stats, key=lambda x: x.overdue_score, reverse=True)[:10]
        
        return {
            'hot_numbers': [
                {'number': s.number, 'score': round(s.hot_score, 2), 'frequency': s.recent_frequency}
                for s in hot_numbers
            ],
            'cold_numbers': [
                {'number': s.number, 'score': round(s.cold_score, 2), 'frequency': s.frequency}
                for s in cold_numbers
            ],
            'overdue_numbers': [
                {'number': s.number, 'score': round(s.overdue_score, 2), 
                 'last_seen': s.last_appearance if s.last_appearance is not None else 'Never'}
                for s in overdue_numbers
            ],
            'patterns': self.analyzer.recent_patterns
        }
    
    def get_top_patterns(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get top N patterns identified from historical data."""
        return self.analyzer.get_top_patterns(n)
