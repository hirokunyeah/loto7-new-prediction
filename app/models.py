"""Data models for Loto7."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class Loto7Draw:
    """Represents a single Loto7 draw."""
    id: str
    date: str
    main: List[int]
    bonus: List[int]
    evaluation: Optional[Dict[str, Any]] = field(default=None)

    def to_dict(self):
        """Convert to dictionary."""
        result = {
            'id': self.id,
            'date': self.date,
            'main': self.main,
            'bonus': self.bonus
        }
        if self.evaluation:
            result['evaluation'] = self.evaluation
        return result

    @staticmethod
    def from_dict(data: dict):
        """Create from dictionary."""
        return Loto7Draw(
            id=data['id'],
            date=data['date'],
            main=data['main'],
            bonus=data['bonus'],
            evaluation=data.get('evaluation')
        )

    def validate(self) -> bool:
        """Validate the draw data."""
        # Check main numbers
        if len(self.main) != 7:
            return False
        if not all(1 <= n <= 37 for n in self.main):
            return False
        if len(set(self.main)) != 7:  # Check for duplicates
            return False
        
        # Check bonus numbers
        if len(self.bonus) != 2:
            return False
        if not all(1 <= n <= 37 for n in self.bonus):
            return False
        if len(set(self.bonus)) != 2:  # Check for duplicates
            return False
        
        # Check overlap between main and bonus
        if set(self.main) & set(self.bonus):
            return False
        
        return True
