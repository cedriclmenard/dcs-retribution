import { AppDispatch } from "../app/store";
import backend from "./backend";
import Combat from "./combat";
import { endCombat, newCombat, updateCombat } from "./combatSlice";
import { updateControlPoint } from "./controlPointsSlice";
import { ControlPoint } from "./controlpoint";
import { Flight } from "./flight";
import {
  deselectFlight,
  registerFlight,
  selectFlight,
  unregisterFlight,
  updateFlight,
  updateFlightPosition,
} from "./flightsSlice";
import {
  addFrontLine,
  deleteFrontLine,
  updateFrontLine,
} from "./frontLinesSlice";
import FrontLine from "./frontline";
import Tgo from "./tgo";
import { updateTgo } from "./tgosSlice";
import { LatLng } from "leaflet";

interface GameUpdateEvents {
  updated_flight_positions: { [id: string]: LatLng };
  new_combats: Combat[];
  updated_combats: Combat[];
  ended_combats: string[];
  navmesh_updates: boolean[];
  unculled_zones_updated: boolean;
  threat_zones_updated: boolean;
  new_flights: Flight[];
  updated_flights: string[];
  deleted_flights: string[];
  selected_flight: string | null;
  deselected_flight: boolean;
  new_front_lines: FrontLine[];
  updated_front_lines: string[];
  deleted_front_lines: string[];
  updated_tgos: string[];
  updated_control_points: number[];
}

export const handleStreamedEvents = (
  dispatch: AppDispatch,
  events: GameUpdateEvents
) => {
  for (const [id, position] of Object.entries(
    events.updated_flight_positions
  )) {
    dispatch(updateFlightPosition([id, position]));
  }

  for (const combat of events.new_combats) {
    dispatch(newCombat(combat));
  }

  for (const combat of events.updated_combats) {
    dispatch(updateCombat(combat));
  }

  for (const id of events.ended_combats) {
    dispatch(endCombat(id));
  }

  for (const flight of events.new_flights) {
    dispatch(registerFlight(flight));
  }

  for (const id of events.updated_flights) {
    backend.get(`/flights/${id}?with_waypoints=true`).then((response) => {
      const flight = response.data as Flight;
      dispatch(updateFlight(flight));
    });
  }

  for (const id of events.deleted_flights) {
    dispatch(unregisterFlight(id));
  }

  if (events.deselected_flight) {
    dispatch(deselectFlight());
  }

  if (events.selected_flight != null) {
    dispatch(selectFlight(events.selected_flight));
  }

  for (const front of events.new_front_lines) {
    dispatch(addFrontLine(front));
  }

  for (const id of events.updated_front_lines) {
    backend.get(`/front-lines/${id}`).then((response) => {
      const front = response.data as FrontLine;
      dispatch(updateFrontLine(front));
    });
  }

  for (const id of events.deleted_front_lines) {
    dispatch(deleteFrontLine(id));
  }

  for (const id of events.updated_tgos) {
    backend.get(`/tgos/${id}`).then((response) => {
      const tgo = response.data as Tgo;
      dispatch(updateTgo(tgo));
    });
  }

  for (const id of events.updated_control_points) {
    backend.get(`/control-points/${id}`).then((response) => {
      const cp = response.data as ControlPoint;
      dispatch(updateControlPoint(cp));
    });
  }
};