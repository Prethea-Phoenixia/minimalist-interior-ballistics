import logging

from a_19 import a_19
from ballistics.gun import Gun
from bs_3 import bs_3
from zis_3 import zis_3

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
    guns.append(zis_3)
    guns.append(bs_3)
    guns.append(a_19)

    Gun.to_file(guns=guns, filename="example_guns.json")
    logger.info("Ended")
