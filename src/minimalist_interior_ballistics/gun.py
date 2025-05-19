from __future__ import annotations

import json
import logging
from bisect import insort
from functools import cached_property
from math import inf
from typing import Callable, Dict, Iterable, Optional, Tuple

from attrs import field, frozen
from cattrs import Converter

from . import DEFAULT_ACC, DEFAULT_GUN_LOSS_FRACTION, DEFAULT_GUN_START_PRESSURE, DEFAULT_STEPS, MAX_DT, Significance
from .charge import Charge
from .num import dekker, gss_max
from .state import State, StateList, StateVector

logger = logging.getLogger(__name__)


@frozen(kw_only=True)
class Gun:
    """
    Class that tracks physical properties of the bore (i.e. that are charge-invariant)
    and manages propellant charge.
    """

    name: str = field(factory=str)
    description: str = field(factory=str)
    family: str = field(factory=str)
    cross_section: float
    shot_mass: float

    charge: Optional[Charge] = None
    charges: tuple[Charge, ...] | list[Charge] = tuple()

    charge_mass: float = 0.0
    charge_masses: tuple[float, ...] | list[float] = tuple()

    chamber_volume: float
    loss_fraction: float = DEFAULT_GUN_LOSS_FRACTION
    start_pressure: float = DEFAULT_GUN_START_PRESSURE
    travel: float = 0.0

    def __attrs_post_init__(self):
        if self.charge and self.charge_mass:
            object.__setattr__(self, "charges", tuple([self.charge]))
            object.__setattr__(self, "charge_masses", tuple([self.charge_mass]))

        elif self.charges and self.charge_masses:
            pass

        else:
            raise ValueError("invalid parameters.")

    def to_json(self):
        converter = Converter()
        return converter.unstructure(self)

    @staticmethod
    def from_json(json_dict: Dict) -> Gun:
        converter = Converter()
        return converter.structure(json_dict, Gun)

    @staticmethod
    def to_file(guns: Iterable[Gun], filename: str):
        with open(filename, mode="w", encoding="utf-8") as f:
            json.dump([gun.to_json() for gun in guns], f, ensure_ascii=False, indent="\t")

    @staticmethod
    def from_file(filename: str) -> Tuple[Gun, ...]:
        guns = []
        with open(filename, mode="r", encoding="utf-8") as f:
            for json_dict in json.load(f):
                guns.append(Gun.from_json(json_dict))

        return tuple(guns)

    @cached_property
    def l_0(self) -> float:
        return self.chamber_volume / self.S

    @cached_property
    def S(self) -> float:
        return self.cross_section

    @cached_property
    def gross_charge_mass(self):
        return sum(self.charge_masses)

    @cached_property
    def delta(self) -> float:
        return self.gross_charge_mass / self.chamber_volume

    @cached_property
    def charge_volume(self) -> float:
        return sum(charge_mass / charge.density for charge, charge_mass in zip(self.charges, self.charge_masses))

    @cached_property
    def phi(self) -> float:
        return 1 + self.loss_fraction + self.gross_charge_mass / (3 * self.shot_mass)

    @cached_property
    def phi_1(self) -> float:
        return 1 + self.loss_fraction

    @cached_property
    def bomb_free_fraction(self) -> float:
        return (
            1
            - sum(charge.covolume * charge_mass for charge, charge_mass in zip(self.charges, self.charge_masses))
            / self.chamber_volume
        )

    @cached_property
    def theta(self) -> float:
        """
        The mixed gas's adiabatic index is assumed to equal that of the primary charge.
        """
        max_charge_mass = max(self.charge_masses)
        charge = self.charges[self.charge_masses.index(max_charge_mass)]
        return charge.adiabatic_index - 1  # catchall.

    @cached_property
    def asymptotic_velocity(self) -> float:
        return (
            (2 * sum(charge.force * charge_mass for charge, charge_mass in zip(self.charges, self.charge_masses)))
            / (self.theta * self.phi * self.shot_mass)
        ) ** 0.5

    def get_thermal_efficiency(self, velocity: float) -> float:
        return (velocity / self.asymptotic_velocity) ** 2

    def get_ballistic_efficiency(self, velocity: float) -> float:
        return self.get_thermal_efficiency(velocity) / self.phi

    def get_piezoelectric_efficiency(self, travel: float, velocity: float, peak_average_pressure: float) -> float:
        return (0.5 * self.phi * self.shot_mass * velocity**2) / (self.cross_section * travel * peak_average_pressure)

    def get_bomb_state(self) -> State:
        """
        Generate a special state that corresponds to the case where the gun is operated
        as a ballistic bomb, and where all propellants have fully combusted. This
        `ballistic.state.State` is uniquely marked by a `ballistic.Significance.BOMB`
        marker. This state's pressure values represents the maximum possible that can
        be achieved under this loading condition regardless of powder combustion behavior.

        """
        return State(
            gun=self,
            sv=StateVector(time=0, travel=0, velocity=0, burnup_fractions=tuple(charge.Z_k for charge in self.charges)),
            marker=Significance.BOMB,
        )

    def get_start_state(self, n_intg: int = DEFAULT_STEPS, acc: float = DEFAULT_ACC) -> State:
        return self.to_start(n_intg=n_intg, acc=acc).get_state_by_marker(significance=Significance.START)

    def gas_energy(self, *, psis: tuple[float, ...], v: float) -> float:

        g_e = -0.5 * self.theta * self.phi * self.shot_mass * v**2
        for charge, charge_mass, psi in zip(self.charges, self.charge_masses, psis):
            g_e += charge.force * charge_mass * psi

        return g_e

    def incompressible_fraction(self, psis: tuple[float, ...]) -> float:
        incompressible_fraction: float = 0.0
        for charge, charge_mass, psi in zip(self.charges, self.charge_masses, psis):
            delta = charge_mass / self.chamber_volume
            incompressible_fraction += delta / charge.density * (1 - psi) + charge.covolume * delta * psi

        return incompressible_fraction

    def dt(self, state: State) -> StateVector:
        P = state.average_pressure
        dZs = tuple(charge.dZdt(P) for charge in self.charges)
        return StateVector(
            time=1,
            travel=state.velocity if state.is_started else 0,
            velocity=(self.S * P / (self.phi * self.shot_mass) if state.is_started else 0),
            burnup_fractions=dZs,
        )

    def dl(self, state: State) -> StateVector:
        # d/dl = d/dt * dt/dl
        # dt / dl = 1/v
        v = state.velocity
        dt = self.dt(state)

        return dt / v

    def dv(self, state: State) -> StateVector:
        # d / dv = d/dt * dt/dv
        dt = self.dt(state)
        return dt / dt.velocity

    def propagate_rk4_in_time(self, state: State, dt: float, marker: Significance = Significance.STEP) -> State:
        return self.propagate_rk4(state=state, s_i=state.increment_time, df=self.dt, dx=dt, marker=marker)

    def propagate_rk4_in_travel(self, state: State, dl: float, marker: Significance = Significance.STEP) -> State:
        return self.propagate_rk4(state=state, s_i=state.increment_travel, df=self.dl, dx=dl, marker=marker)

    def propagate_rk4_in_velocity(self, state: State, dv: float, marker: Significance = Significance.STEP) -> State:
        return self.propagate_rk4(state=state, s_i=state.increment_velocity, df=self.dv, dx=dv, marker=marker)

    def propagate_rk4(
        self,
        state: State,
        s_i: Callable[[StateVector, float, Significance], State],
        df: Callable[[State], StateVector],
        dx: float,
        marker: Significance,
    ) -> State:
        # s_i = state.increment

        k1 = df(state)
        k2 = df(s_i(0.5 * k1 * dx, 0.5 * dx, Significance.INTERMEDIATE))
        k3 = df(s_i(0.5 * k2 * dx, 0.5 * dx, Significance.INTERMEDIATE))
        k4 = df(s_i(k3 * dx, dx, Significance.INTERMEDIATE))
        return s_i((k1 + k2 * 2 + k3 * 2 + k4) * dx / 6, dx, marker)

    def to_start(self, *, n_intg: int = DEFAULT_STEPS, acc: float = DEFAULT_ACC) -> StateList:
        # sanity check: maximum possible pressure developed is higher than start:
        if self.get_bomb_state().average_pressure < self.start_pressure:
            raise ValueError(
                "projectile cannot be started, the maximum pressure achievable is less\
 insufficient to overcome starting resistance."
            )

        initial_state = State(
            gun=self,
            sv=StateVector(time=0.0, travel=0.0, velocity=0.0, burnup_fractions=tuple(0 for _ in self.charges)),
            marker=Significance.IGNITION,
            is_started=False,
        )

        delta_t, rough_ttb = MAX_DT, 0.0
        states = StateList()

        s_now = s_next = initial_state

        while len(states) < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg

            s_next = initial_state
            states = StateList([s_next])

            while s_next.average_pressure < self.start_pressure:
                states.append(s_now := s_next)
                s_next = self.propagate_rk4_in_time(s_now, dt=delta_t)

            rough_ttb = s_next.time

        def state_at_time(time: float, marker: Significance = Significance.INTERMEDIATE) -> State:
            return self.propagate_rk4_in_time(s_now, dt=time - s_now.time, marker=marker)

        start_time, _ = dekker(
            f=lambda t: state_at_time(t).average_pressure - self.start_pressure,
            x_0=s_now.time,
            x_1=s_next.time,
            tol=rough_ttb * acc,
        )

        s_start = state_at_time(time=start_time, marker=Significance.START)
        states.append(s_start)

        return states

    def get_velocity_post_burnout(self, *, burnout_state: State, travel: float) -> float:
        l_k, v_k = burnout_state.travel, burnout_state.velocity
        l_1 = self.l_0 * (1 - self.incompressible_fraction(tuple(1 for _ in self.charges)))
        v_j = self.asymptotic_velocity
        theta = self.theta

        return (1 - (1 - (v_k / v_j) ** 2) / ((l_1 + travel) / (l_1 + l_k)) ** theta) ** 0.5 * v_j

    def get_travel_post_burnout(self, *, burnout_state: State, velocity: float) -> float:
        l_k, v_k = burnout_state.travel, burnout_state.velocity
        l_1 = self.l_0 * (1 - self.incompressible_fraction(tuple(1 for _ in self.charges)))
        v_j = self.asymptotic_velocity
        theta = self.theta

        return (l_1 + l_k) * ((1 - (velocity / v_j) ** 2) / (1 - (v_k / v_j) ** 2)) ** (-1 / theta) - l_1

    def to_burnout(
        self,
        n_intg: int = DEFAULT_STEPS,
        acc: float = DEFAULT_ACC,
        abort_velocity: float = inf,
        abort_travel: float = inf,
    ) -> StateList:
        """
        Integrates projectile motion up to the propellant burnout point and returns
        a List of State.

        Parameters
        ----------
        n_intg: int
            minimum number of integration steps that is to be taken from shot start
            to charge burnout.
        acc: float
            relative accuracy characteristic points (burnout and peak) will be
            determined to in relation to the process's total time. Also controls
            the accuracy to which initial burnup is solved to.
        abort_travel, abort_velocity: float
            additional criteria to abort the calculation before burnout point is
            reached.

        Returns
        -------
        list of `minimalist_interior_ballistics.state.State`.

        Notes
        -----
        Implementation wise, the adaptive step size is first seeded with a
        value from module wide constant `minimalist_interior_ballistics.MAX_DT`, integrated until
        post burnout, or after the abort conditionals (travel or velocity) have been
        exceeded. The total time of which is used as a better approximate to
        time-to-burnout (or abort), divided by `n_intg` as the step size for the next run.
        This is repeated until at least `n_intg` steps were taken (including the
        initial step, and the post-burnout/abort step).

        In the burnout case, the last two steps brackets the actual burnout point,
        from which `minimalist_interior_ballistics.num.dekker` is called to numerically find the burnout
        point to an accuracy of `acc` times the approximate total time.

        In the abort case, the last step is dropped such that the returned
        `minimalist_interior_ballistics.state.StateList` does not contain any point that exceeds the abort
        criteria, whether travel or velocity.

        In either case, the result is passed through `Gun.mark_max_pressure` to mark
        the peak pressure point.
        """
        s_now = s_next = start_state = self.get_start_state(n_intg=n_intg, acc=acc)
        Z_c0s = start_state.burnup_fractions

        def abort(state: State) -> bool:
            return state.travel > abort_travel or state.velocity > abort_velocity

        states = StateList()
        delta_t = MAX_DT
        rough_ttb = 0.0
        while len(states) < n_intg:
            if rough_ttb > 0:
                delta_t = rough_ttb / n_intg
            states = StateList()
            s_next = State(
                gun=self,
                sv=StateVector(time=0.0, travel=0.0, velocity=0.0, burnup_fractions=Z_c0s),
                marker=Significance.START,
            )

            while not (s_next.is_burnout or abort(s_next)):
                states.append(s_now := s_next)
                s_next = self.propagate_rk4_in_time(s_now, dt=delta_t)

            rough_ttb = s_next.time

        def time_end(time: float) -> float:
            s = self.propagate_rk4_in_time(s_now, dt=time - s_now.time)
            return -1 if (s.is_burnout or abort(s)) else 1

        end_time = max(dekker(f=time_end, x_0=s_now.time, x_1=s_next.time, tol=rough_ttb * acc))

        s_end = self.propagate_rk4_in_time(s_now, dt=end_time - s_now.time)

        if abort(s_end):
            # abort prioritized in case of both abort and burnout.
            pass
        elif s_end.is_burnout:
            s_burnout = State.remark(s_end, new_significance=Significance.BURNOUT)
            states.append(s_burnout)

        return self.mark_max_pressure(states, acc=acc)

    def to_travel(
        self, travel: Optional[float] = None, n_intg: int = DEFAULT_STEPS, acc: float = DEFAULT_ACC
    ) -> StateList:
        """
        Conducts integration up to the desired shot-travel using time-wise ODE, if
        the travel is greater than burnout point. Then, length-wise ODE is used
        to single-step to the specified travel.

        Parameters
        ----------
        travel: float
            the projectile travel to which the integration is done to.
        n_intg, acc: int, float
            see documentation for `Gun.to_burnout`.

        Returns
        -------
        list of `minimalist_interior_ballistics.state.State`.
        """

        travel = travel or self.travel
        if not travel:
            raise ValueError("travel must be supplied either as a parameter or during instance instantiation")

        states = self.to_burnout(n_intg=n_intg, acc=acc, abort_travel=travel)
        state = max(states)

        if states.has_state_with_marker(Significance.BURNOUT):
            burnout_state = states.get_state_by_marker(Significance.BURNOUT)

            # use the analytical function to estimate mv.
            v_muzzle = self.get_velocity_post_burnout(burnout_state=burnout_state, travel=travel)
            v_burnout = burnout_state.velocity

            # estimate the number of steps needed to be taken
            v_average = (v_muzzle + v_burnout) * 0.5
            ttm_est = (travel - burnout_state.travel) / v_average

            """
            use a step size that is the greater of
            > previous step size in `to_burnout`
            > a conservative estimate of the time to muzzle `ttm_est`, divided by `n_intg`.
            """
            dt = max((max(states).time - min(states).time) / len(states), ttm_est / n_intg)

            next_state = self.propagate_rk4_in_time(state, dt=dt)

            while next_state.travel < travel:
                states.append(state := next_state)
                next_state = self.propagate_rk4_in_time(state, dt=dt)

        states.append(self.propagate_rk4_in_travel(state, dl=travel - state.travel, marker=Significance.MUZZLE))

        return self.mark_max_pressure(states, acc=acc)

    # def to_velocity(
    #     self,
    #     velocity: float,
    #     n_intg: int = DEFAULT_STEPS,
    #     acc: float = DEFAULT_ACC,
    # ):
    #
    #     pass

    def mark_max_pressure(self, states: StateList, acc: float = DEFAULT_ACC) -> StateList:
        """
        Finds the maximum pressure point and insert it into a list of
        `minimalist_interior_ballistics.state.State`, passed in as argument.

        Notes
        -----
        Implementation wise, conducts a gold-section search using `minimalist_interior_ballistics.num.gss_max`
        in the interval bracketed by the step before and after the step where maximum
        pressure is recorded. By intercepting the accuracy specification passed to the
        generating functions, the peak-pressure point is determined to (at worst) step size
        times `acc`.

        If a previous round of peak pressure finding is recognized (by the presence
        of the `minimalist_interior_ballistics.Significance.PEAK_PRESSURE` marker).
        """
        if not any(s.marker == Significance.PEAK_PRESSURE for s in states):
            total_time = max(states).time - min(states).time
            pressures = [s.average_pressure for s in states]
            j = pressures.index(max(pressures))

            # find the bracketing points.
            i, k = max(j - 1, 0), min(j + 1, len(states) - 1)

            s_i, s_j, s_k = states[i], states[j], states[k]

            def time_pressure(time: float) -> float:
                if time < s_j.time:
                    p_t = self.propagate_rk4_in_time(s_i, dt=time - s_i.time).average_pressure
                else:
                    p_t = self.propagate_rk4_in_time(s_j, dt=time - s_j.time).average_pressure
                return p_t

            time_p_max = sum(gss_max(f=time_pressure, x_0=s_i.time, x_1=s_k.time, tol=acc * total_time)) * 0.5
            s_p_max = self.propagate_rk4_in_time(s_j, dt=time_p_max - s_j.time, marker=Significance.PEAK_PRESSURE)

            insort(states, s_p_max)

        return states
