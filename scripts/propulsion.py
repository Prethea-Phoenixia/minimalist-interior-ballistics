from minimalist_interior_ballistics import Charge, Gun, FormFunction, Propellant
from minimalist_interior_ballistics.design import FixedVolumeDesign
from minimalist_interior_ballistics.problem import FixedVolumeProblem, PressureTarget

gau_propellant = Propellant(
    density=1600,
    force=950000 * 0.981,
    pressure_exponent=1,
    adiabatic_index=1.2,
    covolume=0.001,
    burn_rate_coefficient=5.6e-7,
)

gau_form_function = FormFunction(chi=1.06, labda=-0.06 / 1.06, mu=0)


zis_2_kwargs = {
    "propellant": gau_propellant,
    "form_function": gau_form_function,
    "chamber_volume": 1.875e-3,
    "cross_section": 0.2663e-2,
    "shot_mass": 3.75,
    "travel": 35.66e-1,
    "loss_fraction": 0.03,
    "start_pressure": 300 * 9.81e4,
}


fvp = FixedVolumeProblem(**zis_2_kwargs)
result = fvp.solve_charge_mass_at_pressure_for_velocity(
    pressure_target=PressureTarget.average_pressure(1800 * 9.81e4), velocity_target=700
)

print(result)

print(result[0].to_travel().tabulate())
