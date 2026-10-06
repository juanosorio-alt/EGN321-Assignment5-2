"""Run the Assignment 5.2 CSV replay integration."""

from pathlib import Path
from src.sensor_integration import replay_csv

INPUT = Path("data/readings_failure_scenario.csv")
OUTPUT = Path("output/integration_log.csv")
VALVE_FAMILY = "VX-200"

if __name__ == "__main__":
    rows = replay_csv(INPUT, OUTPUT, valve_family=VALVE_FAMILY)
    accepted = sum(r["accepted_status"] == "ACCEPTED" for r in rows)
    rejected = len(rows) - accepted
    calculated = sum(r["engineering_status"] == "CALCULATED" for r in rows)

    print(f"Processed: {len(rows)}")
    print(f"Sensor accepted: {accepted}")
    print(f"Sensor rejected: {rejected}")
    print(f"Engineering results calculated: {calculated}")
    print(f"Trace log: {OUTPUT}")
