import logging
from datetime import datetime
from pathlib import Path

import Experiments.n_game_untrained_players


log_filename = f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=Path('logs') / log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    Experiments.n_game_untrained_players.run(n_players=256, k=8)