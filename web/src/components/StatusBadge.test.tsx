import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "./StatusBadge";

describe("StatusBadge", () => {
  it("renders the correct label for each status", () => {
    const { rerender } = render(<StatusBadge status="active" />);
    expect(screen.getByText("Active")).toBeInTheDocument();

    rerender(<StatusBadge status="idle" />);
    expect(screen.getByText("Idle")).toBeInTheDocument();

    rerender(<StatusBadge status="maintenance" />);
    expect(screen.getByText("Maintenance")).toBeInTheDocument();

    rerender(<StatusBadge status="offline" />);
    expect(screen.getByText("Offline")).toBeInTheDocument();
  });
});
