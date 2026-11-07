import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FuelBadge } from "./FuelBadge";

describe("FuelBadge", () => {
  it("renders a rounded fuel percentage", () => {
    render(<FuelBadge fuelLevel={62.5} lowFuel={false} />);
    expect(screen.getByText("63%")).toBeInTheDocument();
    expect(screen.queryByText("Low fuel")).not.toBeInTheDocument();
  });

  it("shows the low fuel pill when flagged", () => {
    render(<FuelBadge fuelLevel={11} lowFuel />);
    expect(screen.getByText("11%")).toBeInTheDocument();
    expect(screen.getByText("Low fuel")).toBeInTheDocument();
  });

  it("renders a dash when fuel level is unknown", () => {
    render(<FuelBadge fuelLevel={null} lowFuel={false} />);
    expect(screen.getByText("—")).toBeInTheDocument();
  });
});
