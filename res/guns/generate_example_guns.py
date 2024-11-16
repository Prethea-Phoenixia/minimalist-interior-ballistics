import logging
import os
from importlib import import_module

from ballistics.gun import Gun

logger = logging.getLogger(__name__)

if __name__ in {"__main__", "__mp_main__"}:

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Started")

    directory = os.path.dirname(os.path.realpath(__file__))
    family_dict = {}
    for file in os.listdir(directory):
        filename = os.fsdecode(file)

        if filename.startswith("guns_") and filename.endswith(".py"):
            try:
                all_guns = getattr(import_module(filename.strip(".py")), "all_guns")

                for gun in all_guns:
                    if gun.family not in family_dict:
                        family_dict[gun.family] = [gun]
                    else:
                        family_dict[gun.family].append(gun)

            except AttributeError as e:
                logger.warning(e)

    print(family_dict.keys())

    for family, guns in family_dict.items():
        Gun.to_file(guns, filename=f"jsons/{family.replace(' ', '_')}.json")

    logger.info("Ended")
