import logging
from datetime import datetime
from pathlib import Path

import Experiments.academy_dev
import Experiments.n_player_game_first_attempt
import Experiments.n_player_game_punishing_mediator
import Experiments.n_player_game_debug
import Experiments.n_player_visualization


log_filename = f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=Path('logs') / log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Experiments.academy_dev.run(players_num=265)
    Experiments.n_player_game_punishing_mediator.run(num_players=256, k=12)
    # Experiments.n_player_game_debug.run()
    # Experiments.n_player_visualization.run(n_players=256, k=12)
