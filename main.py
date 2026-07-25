import logging
from datetime import datetime
from pathlib import Path

import Experiments.diplom_work_week


log_filename = f"experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=Path('logs') / log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    # Experiments.rational_mediator_test.run(
    #     n_players=256,
    #     k=7
    # )
    Experiments.diplom_work_week.run_rational_mediator(
        n_players=256,
        k=10)
