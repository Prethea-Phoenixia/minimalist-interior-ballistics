import logging

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import (FixedChargeProblem, FixedVolumeProblem,
                                PressureTarget)

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
    p = FixedVolumeProblem(
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

    # g = p.solve_reduced_burn_rate_for_charge_at_pressure(
    #     charge_mass=1.08,
    #     pressure_target=PressureTarget.average_pressure(value=268e6),
    #     n_intg=100,
    #     acc=1e-4,
    # )

    g = p.solve_charge_mass_at_velocity_and_pressure(
        pressure_target=PressureTarget.average_pressure(value=268e6),
        velocity_target=650,
        n_intg=10,
        acc=1e-3,
    )

    q = FixedChargeProblem(
        cross_section=0.469e-2,
        shot_mass=6.2,
        charge_mass=1.08,
        travel=2.687,
        loss_fraction=0.02,
        start_pressure=30e6,
        propellant=Propellant(
            density=1600,
            force=950000 / 0.98,
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

    q.solve_reduced_burn_rate_for_volume_at_pressure(
        chamber_volume=1.484e-3,
        pressure_target=PressureTarget.average_pressure(value=268e6),
        n_intg=10,
        acc=1e-3,
    )

    print(
        q.solve_chamber_volume_at_velocity_and_pressure(
            pressure_target=PressureTarget.average_pressure(value=268e6),
            velocity_target=680,
            n_intg=10,
            acc=1e-3,
        )
    )

    # Gun.to_file([g, g], "test.json")

    # Gun.from_file(filename="test.json")

    logger.info("ended")


"""
kgf s   9.8 kg m    s           kg
----- = -------- ------- = 980 ----
 dm^2     s^2    0.01m^2        m s
"""
