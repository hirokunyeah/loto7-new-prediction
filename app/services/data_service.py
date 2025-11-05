"""Service for handling Loto7 data operations."""
import json
from typing import List, Optional
from app.models import Loto7Draw


class DataService:
    """Handles Loto7 data loading and saving."""
    
    def __init__(self, data_file_path: str):
        """Initialize with data file path."""
        self.data_file_path = data_file_path
    
    def load_draws(self) -> List[Loto7Draw]:
        """Load draws from JSON file."""
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Loto7Draw.from_dict(draw) for draw in data.get('draws', [])]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
    
    def save_draws(self, draws: List[Loto7Draw]) -> bool:
        """Save draws to JSON file."""
        try:
            data = {'draws': [draw.to_dict() for draw in draws]}
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_latest_draw(self) -> Optional[Loto7Draw]:
        """Get the most recent draw."""
        draws = self.load_draws()
        return draws[0] if draws else None
    
    def get_draws_by_count(self, count: int) -> List[Loto7Draw]:
        """Get the most recent N draws."""
        draws = self.load_draws()
        return draws[:count]
    
    def parse_json_data(self, json_data: dict) -> List[Loto7Draw]:
        """Parse JSON data into Loto7Draw objects."""
        if 'draws' not in json_data or not isinstance(json_data['draws'], list):
            raise ValueError('Invalid JSON format. "draws" array is required.')
        
        draws = []
        for draw_data in json_data['draws']:
            draw = Loto7Draw.from_dict(draw_data)
            if not draw.validate():
                raise ValueError(f'Invalid draw data: {draw.id}')
            draws.append(draw)
        
        return draws
    
    def add_draw(self, new_draw: Loto7Draw) -> bool:
        """Add a new draw to the data file."""
        # Validate the new draw
        if not new_draw.validate():
            raise ValueError(f'Invalid draw data: {new_draw.id}')
        
        # Load existing draws
        draws = self.load_draws()
        
        # Check for duplicate draw ID
        if any(draw.id == new_draw.id for draw in draws):
            raise ValueError(f'Draw with ID {new_draw.id} already exists.')
        
        # Add new draw at the beginning (most recent)
        draws.insert(0, new_draw)
        
        # Save updated draws
        return self.save_draws(draws)
