import logging

from ballistics.charge import Charge
from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import MatchingProblem, Target

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logging.basicConfig(filename="info.log", level=logging.INFO)
    logger.info("Started")
    p = MatchingProblem(
        caliber=76.2e-3,
        shot_mass=6.2,
        chamber_volume=1.484e-3,
        travel=2.687,
        loss_fraction=0.03,
        start_pressure=30e6,
        density=1600,
        force=950000,
        pressure_exponent=0.83,
        covolume=1e-3,
        adiabatic_index=1.2,
        gas_molar_mass=23.55,
        form_function=FormFunction.multi_perf(
            arch_width=10e-3,
            perforation_diameter=5e-3,
            height=0.12,
            n_perforations=7,
        ),
    )

    g = p.solve_reduced_burn_rate(
        mass=1.08,
        # velocity=680,
        pressure=268e6,
        target=Target.AVERAGE,
        n_intg=10,
        acc=1e-3,
    )
    logger.info("ended")

"""
kgf s   9.8 kg m    s           kg
----- = -------- ------- = 980 ----
 dm^2     s^2    0.01m^2        m s
"""
