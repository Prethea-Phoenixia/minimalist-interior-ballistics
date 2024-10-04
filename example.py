import logging

from ballistics.charge import Charge, Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.matching_problem import MatchingProblem, PressureTarget

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Started")
    p = MatchingProblem(
        cross_section=0.469e-2,
        shot_mass=6.2,
        chamber_volume=1.484e-3,
        travel=2.687,
        loss_fraction=0.1,
        start_pressure=30e6,
        propellant=Propellant(
            density=1600,
            force=950000 * 0.98,
            pressure_exponent=0.83,
            covolume=1e-3,
            adiabatic_index=1.2,
        ),
        form_function=FormFunction.multi_perf(
            arch_width=10e-3,
            perforation_diameter=5e-3,
            height=0.12,
            shape=MultiPerfShape.SEVEN_PERF_CYLINDER,
        ),
    )

    _, g = p.solve_reduced_burn_rate(
        mass=1.08,
        pressure_target=PressureTarget.average_pressure(value=268e6),
        n_intg=10,
        acc=1e-4,
    )
    print(g.to_travel(2.687, n_intg=10, acc=1e-4).tabulate())

    logger.info("ended")

"""
kgf s   9.8 kg m    s           kg
----- = -------- ------- = 980 ----
 dm^2     s^2    0.01m^2        m s
"""
