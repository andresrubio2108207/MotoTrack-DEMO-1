from __future__ import annotations

import csv
from pathlib import Path


EXPORT_DIR = Path("exports")


def export_maintenance_history_csv(motorcycle, maintenances, output_dir: Path | str = EXPORT_DIR) -> Path:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    plate = "".join(char for char in str(motorcycle.plate) if char.isalnum() or char in {"-", "_"}).strip() or "moto"
    output_path = target_dir / f"historial_{plate}.csv"

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Moto",
                "Placa",
                "Tipo",
                "Fecha",
                "Km servicio",
                "Costo",
                "Próximo km",
                "Descripción",
            ]
        )
        for item in maintenances:
            writer.writerow(
                [
                    f"{motorcycle.brand} {motorcycle.model}",
                    motorcycle.plate,
                    item.type,
                    item.service_date.isoformat() if item.service_date else "",
                    f"{float(item.km_at_service):.0f}",
                    f"{float(item.cost or 0):.0f}",
                    f"{float(item.next_service_km):.0f}" if item.next_service_km is not None else "",
                    item.description or "",
                ]
            )

    return output_path
