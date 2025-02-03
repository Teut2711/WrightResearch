import pandas as pd


def calculate_broker_score(broker_data):
    # Assign weights to different execution metrics
    weights = {
        "slippage": 0.4,
        "execution_time": 0.3,
        "execution_cost": 0.2,
        "fill_rate": 0.1,
    }

    # Normalize the data (if needed)
    broker_data["normalized_slippage"] = normalize(broker_data["slippage"])
    broker_data["normalized_execution_time"] = normalize(broker_data["execution_time"])
    broker_data["normalized_execution_cost"] = normalize(broker_data["execution_cost"])
    broker_data["normalized_fill_rate"] = normalize(broker_data["fill_rate"])

    # Calculate composite score
    broker_data["score"] = (
        broker_data["normalized_slippage"] * weights["slippage"]
        + broker_data["normalized_execution_time"] * weights["execution_time"]
        + broker_data["normalized_execution_cost"] * weights["execution_cost"]
        + broker_data["normalized_fill_rate"] * weights["fill_rate"]
    )

    return broker_data


def normalize(column):
    return (column - column.min()) / (column.max() - column.min())


# Example broker data
broker_data = pd.DataFrame(
    {
        "broker_id": ["Broker A", "Broker B", "Broker C"],
        "slippage": [0.02, 0.03, 0.01],
        "execution_time": [0.5, 0.6, 0.4],  # in seconds
        "execution_cost": [1.5, 1.8, 1.4],  # in dollars
        "fill_rate": [0.95, 0.92, 0.97],  # percentage
    }
)

# Calculate broker scores
broker_data = calculate_broker_score(broker_data)

# Rank brokers based on the score
broker_data["rank"] = broker_data["score"].rank(ascending=False)

print(broker_data)
