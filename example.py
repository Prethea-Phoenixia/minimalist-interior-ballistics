import logging

from src.ballistics.charge import Charge, Propellant
from src.ballistics.form_function import FormFunction, MultiPerfShape
from src.ballistics.gun import MonoChargeGun
from src.ballistics.problem import (FixedChargeProblem, FixedVolumeProblem,
                                    PressureTarget)
from src.ballistics.state import State, StateList

logger = logging.getLogger(__name__)
dm = 1e-1
dm2 = 1e-2
L = 1e-3
kg_dm3 = 1e3
dm3_kg = 1e-3
kgfdm_kg = 1
kgf_dm2 = 1000  # Pa

dm_s = 0.1  # m/s


if __name__ in {"__main__", "__mp_main__"}:
    logging.basicConfig(
        level=logging.INFO,
        # filename="example.log",
        format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
        datefmt="%Y-%m-%d %H:%M:%S",
        # filemode="w+",
    )
    logger.info("Started")

    tr3 = Propellant(
        name="双芳-3",
        description="",
        density=1.6 * kg_dm3,
        force=950e3 * kgfdm_kg,
        pressure_exponent=0.81,
        covolume=1.0 * dm3_kg,
        adiabatic_index=1.2,
    )
    eighteen_one = FormFunction.single_perf(arch_width=0.85 * 2, height=260)

    g = MonoChargeGun(
        name="BS-3",
        cross_section=0.818 * dm2,
        shot_mass=15.6,
        charge_mass=5.6,
        loss_fraction=0.03,
        start_pressure=30000 * kgf_dm2,
        travel=47.38 * dm,
        charge=Charge.from_propellant(propellant=tr3, form_function=eighteen_one, reduced_burnrate=1),
        chamber_volume=7.9e-3,
    )

    bs_3_fc = FixedChargeProblem(
        name="BS-3",
        cross_section=0.818 * dm2,
        shot_mass=15.6,
        charge_mass=5.6,
        loss_fraction=0.03,
        start_pressure=30000 * kgf_dm2,
        travel=47.38 * dm,
        propellant=tr3,
        form_function=eighteen_one,
    )
    print(PressureTarget.average_pressure.__name__)
    bs_3 = bs_3_fc.solve_reduced_burn_rate_for_volume_at_pressure(
        chamber_volume=7.9 * L,
        pressure_target=PressureTarget.average_pressure(3000e2 * kgf_dm2),
        n_intg=100,
        acc=1e-3,
    )

    print(tr3)
    print(eighteen_one)
    print(bs_3)

    # bs_3_family = GunFamily(name="BS3")
    # bs_3_family.add_gun(bs_3)

    # bs_3_family.to_file("test.json")


"""
kgf s   9.8 kg m    s           kg
----- = -------- ------- = 980 ----
 dm^2     s^2    0.01m^2        m s
"""
