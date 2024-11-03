from statistics import mean

from ballistics.charge import Propellant
from ballistics.form_function import FormFunction, MultiPerfShape
from ballistics.gun import Gun
from ballistics.problem import KnownGunProblem, PressureTarget
from misc import (L, dm, dm2, dm3_kg, format_compo_string, kg_dm3, kgf_dm2,
                  kgfdm_kg)
from prop_7_7 import sb_7_7, seven_seven
from prop_14_7 import fourteen_seven, sb_14_7

zis_s_53_full = KnownGunProblem(
    name="Type 1963 85mm Tank Gun (ZiS-S-53) (WB014P, WB024P HE-Frag, Full)",
    description="Type 1963 85mm tank gun is a domestic produced variant \
of the Soviet 85mm tank gun ZiS-S-53 , with mechanical improvements \
including the addition of fume extractor, and modifications to the \
trunnion to be compatible with stabilizers. Cartridges employ a fixed \
charge design, though the HE-Frag round can be issued with either a Full \
and a Reduced charge. The Full charge is loaded with a central bundle \
of 18/1-42, and loose grains of 14/7, up to a total mass of 2.48-2.63 kg. \n\
This example illustrates the case for the normal HE-Frag shell WB014P, \
or the nodular cast iron shell WB024P, with Full charge. \n\
Additionally, note that the interior ballistics of the ZiS-S-53 is \
identical to that of the Soviet 85mm divisional gun D-44 (including its \
domestic equivalent, Type 1956 85mm cannon), and with \
the Soviet 85mm air defense gun M1939 (52-K). Consequently, data from \
these has been consulted to produce the this example. \n\
The nominal velocity is between 785 - 793 m/s, and nominal pressure of \
2550 kgf/cm^2 from copper crusher gauge, converts to 2687 kgf/cm^2 \
actual. \n\
For simplicity, and in accordance with the treatment detailed in the \
sources, the 18/1-42 bundle is treated as the equivalent of mass in \
14/7, with reasonable accuracy.\n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.582 * dm2,
    shot_mass=9.54,
    charge_mass=2.48,
    chamber_volume=3.8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
    propellant=sb_14_7,
    form_function=fourteen_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2687e2 * kgf_dm2),
)


zis_s_53_reduced = KnownGunProblem(
    name="Type 1963 85mm Tank Gun (ZiS-S-53) (WB014P, WB024P HE-Frag, Reduced)",
    description="Type 1963 85mm tank gun is a domestic produced variant \
of the Soviet 85mm tank gun ZiS-S-53 , with mechanical improvements \
including the addition of fume extractor, and modifications to the \
trunnion to be compatible with stabilizers. Cartridges employ a fixed \
charge design, though the HE-Frag round can be issued with either a Full \
and a Reduced charge. The Reduced charge is loaded with a central bundle \
of 12/1, and loose grains of 7/7, up to a total mass of 1.50 kg. \n\
This example illustrates the case for the normal HE-Frag shell WB014P, \
or the nodular cast iron shell WB024P, with Reduced charge. \n\
Additionally, note that the interior ballistics of the ZiS-S-53 is \
identical to that of the Soviet 85mm divisional gun D-44 (including its \
domestic equivalent, Type 1956 85mm cannon), and with \
the Soviet 85mm air defense gun M1939 (52-K). Consequently, data from \
these has been consulted to produce the this example. \n\
The nominal velocity is 655 m/s, and nominal pressure of \
2350 kgf/cm^2 from copper crusher gauge. \n\
For simplicity, and in accordance with the treatment detailed in the \
sources, the 12/1 bundle is treated as the equivalent of mass in \
7/7, with reasonable accuracy. A pressure of 2285 kgf/cm^2 has \
been adopted to best match the tabulated performance. \n\
Reference:\n\
 《火炮内弹道计算手册》(1987)\n\
 《火炸药手册 (增订本）第二分册》(1981).",
    cross_section=0.582 * dm2,
    shot_mass=9.54,
    charge_mass=1.5,
    chamber_volume=3.8 * L,
    loss_fraction=0.03,
    start_pressure=300e2 * kgf_dm2,
    travel=35.92 * dm,
    propellant=sb_7_7,
    form_function=seven_seven,
).get_gun_developing_pressure(
    pressure_target=PressureTarget.average_pressure(2285e2 * kgf_dm2),
)


if __name__ == "__main__":
    from ballistics.state import StateList

    print(zis_s_53_full.name)
    print(StateList.tabulate(zis_s_53_full.to_travel(n_intg=10)))
    print(zis_s_53_reduced.name)
    print(StateList.tabulate(zis_s_53_reduced.to_travel(n_intg=10)))
