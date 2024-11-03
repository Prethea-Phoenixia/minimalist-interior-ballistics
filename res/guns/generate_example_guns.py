import logging

from a_19 import a_19
from ballistics.gun import Gun
from bs_3 import bs_3
from m_46 import m_46_four, m_46_full, m_46_one, m_46_three, m_46_two
from m_47 import m_47_full, m_47_one
from type_86_152 import (type_86_152_four, type_86_152_full, type_86_152_one,
                         type_86_152_three, type_86_152_two)
from zis_2 import zis_2_apcbc, zis_2_apcr, zis_2_he_frag
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
    guns.append(zis_2_apcr)
    guns.append(zis_2_apcbc)
    guns.append(zis_2_he_frag)
    guns.append(zis_3)

    guns.append(bs_3)
    guns.append(a_19)

    guns.append(m_46_full)
    guns.append(m_46_one)
    guns.append(m_46_two)
    guns.append(m_46_three)
    guns.append(m_46_four)

    guns.append(m_47_full)
    guns.append(m_47_one)

    guns.extend(
        (
            type_86_152_full,
            type_86_152_one,
            type_86_152_two,
            type_86_152_three,
            type_86_152_four,
        )
    )

    Gun.to_file(guns=guns, filename="example_guns.json")
    logger.info("Ended")
