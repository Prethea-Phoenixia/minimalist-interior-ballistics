import logging
import os
from importlib import import_module

from ballistics.gun import Gun

logger = logging.getLogger(__name__)

if __name__ in {"__main__", "__mp_main__"}:

    logging.basicConfig(
        level=logging.INFO,
        # filename="example.log",
        format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
        datefmt="%Y-%m-%d %H:%M:%S",
        # filemode="w+",
    )
    logger.info("Started")

    guns = []

    directory = os.path.dirname(os.path.realpath(__file__))

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.startswith("guns_") and filename.endswith(".py"):
            try:
                all_guns = getattr(import_module(filename.strip(".py")), "all_guns")
                guns.extend(all_guns)

                logger.info(f"read {len(all_guns)} entries from {filename}")
            except AttributeError as e:
                logger.warning(e)

    guns.extend(guns)
    Gun.to_file(guns=guns, filename="example_guns.json")
    logger.info("Ended")
