import logging

from a_19 import a_19
from ballistics.gun import Gun
from bs_3 import bs_3_apbc, bs_3_he_frag
from m_46 import m_46_four, m_46_full, m_46_one, m_46_three, m_46_two
from m_47 import m_47_full, m_47_one, m_47_three, m_47_two
from type_86_100 import type_86_100_w_apfsds
from type_86_152 import (type_86_152_four, type_86_152_full, type_86_152_one,
                         type_86_152_three, type_86_152_two)

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

    # __cannon__

    from zis_2 import all_guns

    guns.extend(all_guns)

    from zis_3 import all_guns

    guns.extend(all_guns)

    guns.append(bs_3_apbc)
    guns.append(bs_3_he_frag)

    guns.append(type_86_100_w_apfsds)

    guns.append(a_19)

    guns.append(m_46_full)
    guns.append(m_46_one)
    guns.append(m_46_two)
    guns.append(m_46_three)
    guns.append(m_46_four)

    guns.append(m_47_full)
    guns.append(m_47_one)
    guns.append(m_47_two)
    guns.append(m_47_three)

    guns.extend(
        (
            type_86_152_full,
            type_86_152_one,
            type_86_152_two,
            type_86_152_three,
            type_86_152_four,
        )
    )

    from family85mm import all_guns

    guns.extend(all_guns)
    Gun.to_file(guns=guns, filename="example_guns.json")
    logger.info("Ended")
