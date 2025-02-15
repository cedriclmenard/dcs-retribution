from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, TYPE_CHECKING, TypeGuard, TypeVar

from game.ato.flightplans.standard import StandardFlightPlan, StandardLayout
from game.typeguard import self_type_guard
from game.utils import Distance, Speed
from .uizonedisplay import UiZone, UiZoneDisplay

if TYPE_CHECKING:
    from ..flightwaypoint import FlightWaypoint
    from .flightplan import FlightPlan


@dataclass
class PatrollingLayout(StandardLayout):
    patrol_start: FlightWaypoint
    patrol_end: FlightWaypoint

    def iter_waypoints(self) -> Iterator[FlightWaypoint]:
        yield self.departure
        yield from self.nav_to
        yield self.patrol_start
        yield self.patrol_end
        yield from self.nav_from
        yield self.arrival
        if self.divert is not None:
            yield self.divert
        yield self.bullseye
        yield from self.custom_waypoints


LayoutT = TypeVar("LayoutT", bound=PatrollingLayout)


class PatrollingFlightPlan(StandardFlightPlan[LayoutT], UiZoneDisplay, ABC):
    @property
    @abstractmethod
    def patrol_duration(self) -> timedelta:
        """Maximum time to remain on station."""

    @property
    @abstractmethod
    def patrol_speed(self) -> Speed:
        """Racetrack speed TAS."""

    @property
    @abstractmethod
    def engagement_distance(self) -> Distance:
        """The maximum engagement distance.

        The engagement range of any Search Then Engage task, or the radius of a Search
        Then Engage in Zone task. Any enemies of the appropriate type for this mission
        within this range of the flight's current position (or the center of the zone)
        will be engaged by the flight.
        """

    @property
    def patrol_start_time(self) -> datetime:
        return self.tot

    @property
    def patrol_end_time(self) -> datetime:
        # TODO: This is currently wrong for CAS.
        # CAS missions end when they're winchester or bingo. We need to
        # configure push tasks for the escorts rather than relying on timing.
        return self.patrol_start_time + self.patrol_duration

    def tot_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        if waypoint == self.layout.patrol_start:
            return self.patrol_start_time
        return None

    def depart_time_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        if waypoint == self.layout.patrol_end:
            return self.patrol_end_time
        return None

    def takeoff_time(self) -> datetime:
        return self.patrol_start_time - self._travel_time_to_waypoint(self.tot_waypoint)

    @property
    def package_speed_waypoints(self) -> set[FlightWaypoint]:
        return {self.layout.patrol_start, self.layout.patrol_end}

    @property
    def tot_waypoint(self) -> FlightWaypoint:
        return self.layout.patrol_start

    @property
    def mission_begin_on_station_time(self) -> datetime | None:
        return self.patrol_start_time

    @property
    def mission_departure_time(self) -> datetime:
        return self.patrol_end_time

    @self_type_guard
    def is_patrol(
        self, flight_plan: FlightPlan[Any]
    ) -> TypeGuard[PatrollingFlightPlan[Any]]:
        return True

    def ui_zone(self) -> UiZone:
        return UiZone(
            [self.layout.patrol_start.position, self.layout.patrol_end.position],
            self.engagement_distance,
        )
