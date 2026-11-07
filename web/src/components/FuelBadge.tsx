import React from "react";

interface Props {
  fuelLevel: number | null;
  lowFuel: boolean;
}

export function FuelBadge({ fuelLevel, lowFuel }: Props) {
  if (fuelLevel == null) return <span className="fuel-level">—</span>;
  return (
    <span className="fuel-level">
      {`${Math.round(fuelLevel)}%`}
      {lowFuel && <span className="fuel-badge low-fuel">Low fuel</span>}
    </span>
  );
}
