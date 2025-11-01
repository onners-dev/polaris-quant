import json
import os
from tabulate import tabulate

REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/registry.json"))

if not os.path.exists(REGISTRY_PATH):
    print("No model registry found.")
    exit(0)

with open(REGISTRY_PATH, "r") as f:
    registry = json.load(f)

rows = []
for m in registry:
    tickers = ", ".join(m.get("tickers")) if isinstance(m.get("tickers"), list) else str(m.get("tickers", ""))
    rows.append([
        m.get("model_id", "")[:16],  # Short ID
        tickers,
        m.get("target", ""),
        m.get("trained_at", "")[:19],
        f"{m.get('test_sharpe', 0):.4f}",
        f"{m.get('test_rmse', 0):.5f}",
        f"{m.get('test_drawdown', 0):.3f}",
        " → ".join(m.get("test_dates", ["", ""])),
        f"{m.get('val_sharpe', 0):.4f}",
        f"{m.get('val_rmse', 0):.5f}",
        " → ".join(m.get("validation_dates", ["", ""])),
        f"{m.get('feature_importances', [])[0]:.3f}" if "feature_importances" in m and len(m["feature_importances"]) > 0 else ""
    ])

if not rows:
    print("No models in registry.")
    exit(0)

rows.sort(key=lambda x: float(x[4]), reverse=True)  # Sort by test_sharpe desc

headers = [
    "Model ID", "Tickers", "Target", "Trained At",
    "Test Sharpe", "Test RMSE", "Test MaxDD", "Test Range",
    "Val Sharpe", "Val RMSE", "Val Range", "Top FeatImpt"
]

print("\nModel Leaderboard (sorted by Test Sharpe)") 
print("=" * 80)
print(tabulate(rows, headers=headers, tablefmt="pretty"))
print("=" * 80)
print(f"Total models in registry: {len(rows)}")
champion = rows[0]
print(f"\nChampion Model: {champion[0]} | {champion[1]} | Test Sharpe: {champion[4]}")
