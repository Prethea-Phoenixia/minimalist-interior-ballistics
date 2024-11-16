import logging
import os
from importlib import import_module

logger = logging.getLogger(__name__)

if __name__ in {"__main__", "__mp_main__"}:

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Started")

    directory = os.path.dirname(os.path.realpath(__file__))

    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.startswith("guns_") and filename.endswith(".py"):
            try:
                family = getattr(import_module(filename.strip(".py")), "family")
                family.to_file(f"jsons/{family.name.replace(' ', '_')}.json")

            except AttributeError as e:
                logger.warning(e)

    logger.info("Ended")
