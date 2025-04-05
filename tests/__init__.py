import logging


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    filename="tests.log",
    format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="w+",
)

dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 0.98
kgf_dm2 = 980
dm_s = 0.1
