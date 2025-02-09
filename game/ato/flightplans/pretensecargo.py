from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Type

from game.utils import feet
from .ferry import FerryLayout
from .ibuilder import IBuilder
from .planningerror import PlanningError
from .standard import StandardFlightPlan, StandardLayout
from .waypointbuilder import WaypointBuilder
from ...theater import OffMapSpawn

if TYPE_CHECKING:
    from ..flightwaypoint import FlightWaypoint


PRETENSE_CARGO_FLIGHT_DISTANCE = 100000
PRETENSE_CARGO_FLIGHT_HEADING_RANGE = 20


class PretenseCargoFlightPlan(StandardFlightPlan[FerryLayout]):
    @staticmethod
    def builder_type() -> Type[Builder]:
        return Builder

    @property
    def tot_waypoint(self) -> FlightWaypoint:
        return self.layout.arrival

    def tot_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        # TOT planning isn't really useful for ferries. They're behind the front
        # lines so no need to wait for escorts or for other missions to complete.
        return None

    def depart_time_for_waypoint(self, waypoint: FlightWaypoint) -> datetime | None:
        return None

    @property
    def mission_begin_on_station_time(self) -> datetime | None:
        return None

    @property
    def mission_departure_time(self) -> datetime:
        return self.package.time_over_target


class Builder(IBuilder[PretenseCargoFlightPlan, FerryLayout]):
    def layout(self) -> FerryLayout:
        # Find the spawn location for off-map transport planes
        distance_to_flot = 0.0
        heading_from_flot = 0.0
        offmap_transport_cp_id = self.flight.departure.id
        for front_line_cp in self.coalition.game.theater.controlpoints:
            if isinstance(front_line_cp, OffMapSpawn):
                continue
            for front_line in self.coalition.game.theater.conflicts():
                if front_line_cp.captured == self.flight.coalition.player:
                    if (
                        front_line_cp.position.distance_to_point(front_line.position)
                        > distance_to_flot
                    ):
                        distance_to_flot = front_line_cp.position.distance_to_point(
                            front_line.position
                        )
                        heading_from_flot = front_line.position.heading_between_point(
                            front_line_cp.position
                        )
                        offmap_transport_cp_id = front_line_cp.id
        offmap_transport_cp = self.coalition.game.theater.find_control_point_by_id(
            offmap_transport_cp_id
        )
        offmap_heading = random.randrange(
            int(heading_from_flot - PRETENSE_CARGO_FLIGHT_HEADING_RANGE),
            int(heading_from_flot + PRETENSE_CARGO_FLIGHT_HEADING_RANGE),
        )
        offmap_transport_spawn = offmap_transport_cp.position.point_from_heading(
            offmap_heading, PRETENSE_CARGO_FLIGHT_DISTANCE
        )

        altitude_is_agl = self.flight.is_helo
        altitude = (
            feet(self.coalition.game.settings.heli_cruise_alt_agl)
            if altitude_is_agl
            else self.flight.unit_type.preferred_patrol_altitude
        )

        builder = WaypointBuilder(self.flight)
        ferry_layout = FerryLayout(
            departure=builder.join(offmap_transport_spawn),
            nav_to=builder.nav_path(
                offmap_transport_spawn,
                self.flight.arrival.position,
                altitude,
                altitude_is_agl,
            ),
            arrival=builder.land(self.flight.arrival),
            divert=builder.divert(self.flight.divert),
            bullseye=builder.bullseye(),
            nav_from=[],
            custom_waypoints=list(),
        )
        ferry_layout.departure = builder.join(offmap_transport_spawn)
        ferry_layout.nav_to.append(builder.join(offmap_transport_spawn))
        ferry_layout.nav_from.append(builder.join(offmap_transport_spawn))
        return ferry_layout

    def build(self, dump_debug_info: bool = False) -> PretenseCargoFlightPlan:
        return PretenseCargoFlightPlan(self.flight, self.layout())
