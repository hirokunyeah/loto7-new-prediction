"""Statistical analyzer for Loto7 predictions with enhanced filtering and scoring."""
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

# Scoring constants
OVERDUE_SCORE_MULTIPLIER = 50
HOT_NUMBER_TARGET_PERCENTAGE = 40
BALANCED_NUMBER_WEIGHT = 0.4
OVERDUE_NUMBER_TARGET_PERCENTAGE = 20
NEUTRAL_FREQUENCY_SCORE = 50.0


@dataclass
class FilterConfig:
    """Configuration for prediction filters."""
    # Continuous numbers filter
    continuous_max: int = 1  # Maximum allowed consecutive pairs
    continuous_weight: float = 10.0
    
    # Zone3 distribution filter (1-12, 13-25, 26-37)
    zone3_required: bool = True  # All zones must be covered
    zone3_weight: float = 15.0
    
    # Zone4 distribution filter (1-9, 10-18, 19-27, 28-37)
    zone4_required: bool = True  # All zones must be covered
    zone4_weight: float = 15.0
    
    # Odd/Even balance filter
    odd_even_balance: Tuple[int, int] = (3, 4)  # (min_odd, max_odd)
    odd_even_weight: float = 10.0
    
    # Sum range filter
    sum_min: int = 100
    sum_max: int = 170
    sum_weight: float = 15.0
    
    # Last digits distribution filter
    last_digit_max_duplicate: int = 2  # Maximum same last digit
    last_digit_weight: float = 10.0
    
    # Pull filter (overlap with previous draw)
    pull_max: int = 1  # Maximum overlap with previous draw
    pull_weight: float = 10.0
    
    # Frequency analysis weight
    frequency_weight: float = 15.0


@dataclass
class StatisticalMetrics:
    """Statistical metrics for number analysis."""
    number: int
    frequency: int = 0  # How many times appeared
    recent_frequency: int = 0  # Frequency in recent N draws
    last_appearance: Optional[int] = None  # Draws since last appearance
    hot_score: float = 0.0  # Score for "hot" numbers
    cold_score: float = 0.0  # Score for "cold" numbers
    overdue_score: float = 0.0  # Score for overdue numbers


class StatisticalAnalyzer:
    """Enhanced statistical analyzer for Loto7 predictions."""
    
    def __init__(self, config: Optional[FilterConfig] = None):
        """Initialize with optional custom configuration."""
        self.config = config or FilterConfig()
        self.historical_stats: Dict[int, StatisticalMetrics] = {}
        self.recent_patterns: List[Dict[str, Any]] = []
        
    def analyze_historical_data(self, draws: List[Any], recent_window: int = 10) -> None:
        """Analyze historical draw data for statistical insights."""
        # Initialize metrics for all numbers
        for num in range(1, 38):
            self.historical_stats[num] = StatisticalMetrics(number=num)
        
        # Analyze each draw
        all_numbers = []
        for i, draw in enumerate(draws):
            numbers = draw.main if hasattr(draw, 'main') else draw['main']
            all_numbers.extend(numbers)
            
            # Update frequency and last appearance
            for num in numbers:
                self.historical_stats[num].frequency += 1
                if i < recent_window:
                    self.historical_stats[num].recent_frequency += 1
                if self.historical_stats[num].last_appearance is None:
                    self.historical_stats[num].last_appearance = i
        
        # Calculate hot/cold/overdue scores
        if draws:
            total_draws = len(draws)
            for num in range(1, 38):
                stats = self.historical_stats[num]
                
                # Hot score: based on recent frequency
                stats.hot_score = (stats.recent_frequency / min(recent_window, total_draws)) * 100
                
                # Cold score: inverse of overall frequency
                avg_frequency = sum(s.frequency for s in self.historical_stats.values()) / 37
                stats.cold_score = max(0, (avg_frequency - stats.frequency) / avg_frequency * 100) if avg_frequency > 0 else 0
                
                # Overdue score: based on time since last appearance
                if stats.last_appearance is not None:
                    expected_gap = total_draws / (stats.frequency if stats.frequency > 0 else 1)
                    actual_gap = stats.last_appearance
                    stats.overdue_score = min(100, (actual_gap / expected_gap * OVERDUE_SCORE_MULTIPLIER)) if expected_gap > 0 else 0
                else:
                    stats.overdue_score = 100  # Never appeared
    
    def score_combination(
        self,
        combo: Tuple[int, ...],
        evaluation: Dict[str, Any],
        previous_draw_numbers: set = None
    ) -> Dict[str, Any]:
        """Score a combination based on multiple criteria (0-100 scale)."""
        scores = {}
        total_weight = 0.0
        weighted_sum = 0.0
        
        # Score each filter criterion
        # 1. Continuous numbers
        continuous_pass = evaluation['continuous']['pass']
        continuous_score = 100.0 if continuous_pass else 0.0
        scores['continuous'] = continuous_score
        weighted_sum += continuous_score * self.config.continuous_weight
        total_weight += self.config.continuous_weight
        
        # 2. Zone3 distribution
        zone3_pass = evaluation['zone3']['pass']
        zone3_score = 100.0 if zone3_pass else 0.0
        scores['zone3'] = zone3_score
        weighted_sum += zone3_score * self.config.zone3_weight
        total_weight += self.config.zone3_weight
        
        # 3. Zone4 distribution
        zone4_pass = evaluation['zone4']['pass']
        zone4_score = 100.0 if zone4_pass else 0.0
        scores['zone4'] = zone4_score
        weighted_sum += zone4_score * self.config.zone4_weight
        total_weight += self.config.zone4_weight
        
        # 4. Odd/Even balance
        odd_even_pass = evaluation['odd_even']['pass']
        odd_even_score = 100.0 if odd_even_pass else 0.0
        scores['odd_even'] = odd_even_score
        weighted_sum += odd_even_score * self.config.odd_even_weight
        total_weight += self.config.odd_even_weight
        
        # 5. Sum range
        sum_pass = evaluation['sum']['pass']
        sum_score = 100.0 if sum_pass else 0.0
        scores['sum'] = sum_score
        weighted_sum += sum_score * self.config.sum_weight
        total_weight += self.config.sum_weight
        
        # 6. Last digits
        last_digit_pass = evaluation['last_digits']['pass']
        last_digit_score = 100.0 if last_digit_pass else 0.0
        scores['last_digits'] = last_digit_score
        weighted_sum += last_digit_score * self.config.last_digit_weight
        total_weight += self.config.last_digit_weight
        
        # 7. Pull filter
        pull_pass = evaluation['pull']['pass']
        pull_score = 100.0 if pull_pass else 0.0
        scores['pull'] = pull_score
        weighted_sum += pull_score * self.config.pull_weight
        total_weight += self.config.pull_weight
        
        # 8. Frequency analysis (if historical stats available)
        if self.historical_stats:
            frequency_score = self._calculate_frequency_score(combo)
            scores['frequency'] = frequency_score
            weighted_sum += frequency_score * self.config.frequency_weight
            total_weight += self.config.frequency_weight
        
        # Calculate final score (0-100)
        final_score = (weighted_sum / total_weight) if total_weight > 0 else 0.0
        
        return {
            'scores': scores,
            'final_score': round(final_score, 2),
            'weights': {
                'continuous': self.config.continuous_weight,
                'zone3': self.config.zone3_weight,
                'zone4': self.config.zone4_weight,
                'odd_even': self.config.odd_even_weight,
                'sum': self.config.sum_weight,
                'last_digits': self.config.last_digit_weight,
                'pull': self.config.pull_weight,
                'frequency': self.config.frequency_weight if self.historical_stats else 0.0
            }
        }
    
    def _calculate_frequency_score(self, combo: Tuple[int, ...]) -> float:
        """Calculate frequency-based score for a combination."""
        if not self.historical_stats:
            return NEUTRAL_FREQUENCY_SCORE  # Neutral score
        
        # Balance hot, cold, and overdue numbers
        hot_avg = sum(self.historical_stats[n].hot_score for n in combo) / 7
        cold_avg = sum(self.historical_stats[n].cold_score for n in combo) / 7
        overdue_avg = sum(self.historical_stats[n].overdue_score for n in combo) / 7
        
        # Optimal balance: mix of hot, balanced, and overdue numbers
        balance_score = (
            min(hot_avg / HOT_NUMBER_TARGET_PERCENTAGE, 1.0) * HOT_NUMBER_TARGET_PERCENTAGE +
            (100 - abs(NEUTRAL_FREQUENCY_SCORE - cold_avg)) * BALANCED_NUMBER_WEIGHT +
            min(overdue_avg / OVERDUE_NUMBER_TARGET_PERCENTAGE, 1.0) * OVERDUE_NUMBER_TARGET_PERCENTAGE
        )
        
        return min(100.0, balance_score)
    
    def identify_patterns(self, draws: List[Any]) -> List[Dict[str, Any]]:
        """Identify common patterns in historical draws."""
        patterns = []
        
        if len(draws) < 3:
            return patterns
        
        # Pattern 1: Consecutive numbers frequency
        consecutive_counts = []
        for draw in draws[:10]:  # Recent 10 draws
            numbers = draw.main if hasattr(draw, 'main') else draw['main']
            sorted_nums = sorted(numbers)
            consecutive = sum(1 for i in range(len(sorted_nums)-1) 
                            if sorted_nums[i] + 1 == sorted_nums[i+1])
            consecutive_counts.append(consecutive)
        
        avg_consecutive = sum(consecutive_counts) / len(consecutive_counts)
        patterns.append({
            'type': 'consecutive',
            'description': f'Average {avg_consecutive:.1f} consecutive pairs in recent draws',
            'value': avg_consecutive
        })
        
        # Pattern 2: Zone distribution preference
        zone_distributions = {'low': 0, 'mid': 0, 'high': 0}
        for draw in draws[:10]:
            numbers = draw.main if hasattr(draw, 'main') else draw['main']
            for num in numbers:
                if 1 <= num <= 12:
                    zone_distributions['low'] += 1
                elif 13 <= num <= 25:
                    zone_distributions['mid'] += 1
                else:
                    zone_distributions['high'] += 1
        
        total = sum(zone_distributions.values())
        patterns.append({
            'type': 'zone_distribution',
            'description': 'Zone distribution in recent draws',
            'value': {k: round(v/total*100, 1) for k, v in zone_distributions.items()}
        })
        
        # Pattern 3: Odd/Even ratio
        odd_even_ratios = []
        for draw in draws[:10]:
            numbers = draw.main if hasattr(draw, 'main') else draw['main']
            odd_count = sum(1 for n in numbers if n % 2 != 0)
            odd_even_ratios.append(odd_count)
        
        avg_odd = sum(odd_even_ratios) / len(odd_even_ratios)
        patterns.append({
            'type': 'odd_even_ratio',
            'description': f'Average {avg_odd:.1f} odd numbers in recent draws',
            'value': avg_odd
        })
        
        self.recent_patterns = patterns
        return patterns
    
    def rank_predictions(
        self,
        predictions: List[Tuple[Any, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Rank predictions by score and return top results."""
        # Filter out predictions without scoring
        predictions_with_scores = [
            (combo, data) for combo, data in predictions
            if data.get('scoring') is not None
        ]
        
        if not predictions_with_scores:
            # If no scores, return unranked
            return [
                {
                    'rank': i + 1,
                    'combination': list(combo),
                    'score': None,
                    'evaluation': data.get('evaluation'),
                    'scoring': None
                }
                for i, (combo, data) in enumerate(predictions)
            ]
        
        # Sort by final score (descending)
        ranked = sorted(
            predictions_with_scores,
            key=lambda x: x[1]['scoring']['final_score'],
            reverse=True
        )
        
        results = []
        for rank, (combo, data) in enumerate(ranked, 1):
            results.append({
                'rank': rank,
                'combination': list(combo),
                'score': data['scoring']['final_score'],
                'evaluation': data['evaluation'],
                'scoring': data['scoring']
            })
        
        return results
    
    def get_top_patterns(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get top N patterns from recent analysis."""
        return self.recent_patterns[:n]
