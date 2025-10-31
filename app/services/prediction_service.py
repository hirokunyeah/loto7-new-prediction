"""Service for generating Loto7 number predictions."""
import random
from typing import List, Set, Tuple, Optional
from collections import Counter
from datetime import datetime, timedelta
from app.models import Loto7Draw


class PredictionService:
    """Handles Loto7 number prediction logic."""
    
    def __init__(self, previous_draw: Optional[Loto7Draw] = None):
        """Initialize prediction service."""
        self.previous_draw_numbers = set()
        if previous_draw:
            self.previous_draw_numbers = set(previous_draw.main + previous_draw.bonus)
        
        # Filter settings
        self.sum_min = 100
        self.sum_max = 170
    
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
        start_draw_number: int = 650
    ) -> List[Loto7Draw]:
        """Create Loto7Draw objects from predictions."""
        draws = []
        base_date = datetime.now()
        
        for i, combo in enumerate(predictions):
            draw_id = f"第{start_draw_number + i}回"
            draw_date = (base_date + timedelta(weeks=i)).strftime("%Y-%m-%d")
            bonus_numbers = self.generate_bonus_numbers(list(combo))
            
            draw = Loto7Draw(
                id=draw_id,
                date=draw_date,
                main=list(combo),
                bonus=bonus_numbers
            )
            draws.append(draw)
        
        return draws
