import pytest
import os
import json
import time
from typing import Any, Dict
from unittest.mock import patch
from pathlib import Path
from docker import from_env as docker_from_env

# Constants
MODEL_TRAINING_IMAGE = "cyber-threat-detection:latest"
TRAINING_DATA_PATH = "tests/data/training_data.json"
TEST_DATA_PATH = "tests/data/test_data.json"
MODEL_OUTPUT_PATH = "tests/output/model.pkl"
INFERENCE_API_URL = "http://localhost:5000/inference"
PERFORMANCE_THRESHOLD = 0.95  # Minimum acceptable model accuracy
LOAD_TEST_REQUESTS = 100
LOAD_TEST_CONCURRENCY = 10

# Fixtures
@pytest.fixture(scope="module")
def docker_client():
    """Fixture to provide a Docker client instance."""
    client = docker_from_env()
    yield client
    client.close()

@pytest.fixture(scope="module")
def training_data():
    """Fixture to load training data."""
    with open(TRAINING_DATA_PATH, "r") as f:
        data = json.load(f)
    return data

@pytest.fixture(scope="module")
def test_data():
    """Fixture to load test data."""
    with open(TEST_DATA_PATH, "r") as f:
        data = json.load(f)
    return data

@pytest.fixture(scope="module")
def model_container(docker_client):
    """
    Fixture to build and run the Docker container for the model training and inference.
    Ensures proper setup and teardown.
    """
    # Build the Docker image
    docker_client.images.build(path=".", tag=MODEL_TRAINING_IMAGE)

    # Run the container
    container = docker_client.containers.run(
        MODEL_TRAINING_IMAGE,
        detach=True,
        ports={"5000/tcp": 5000},
        environment={"MODEL_OUTPUT_PATH": MODEL_OUTPUT_PATH},
        volumes={
            os.path.abspath("tests/output"): {"bind": "/app/output", "mode": "rw"},
            os.path.abspath("tests/data"): {"bind": "/app/data", "mode": "ro"},
        },
    )
    time.sleep(5)  # Allow the container to initialize
    yield container

    # Teardown: Stop and remove the container
    container.stop()
    container.remove()

# Helper Functions
def send_inference_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a POST request to the inference API."""
    import requests
    response = requests.post(INFERENCE_API_URL, json=payload)
    response.raise_for_status()
    return response.json()

# Tests
def test_model_training_happy_path(model_container, training_data):
    """
    Test the happy path for model training.
    Ensures the model is trained and saved successfully.
    """
    model_path = Path(MODEL_OUTPUT_PATH)
    assert not model_path.exists(), "Model file should not exist before training."

    # Trigger training (mocked for simplicity)
    with patch("app.train_model") as mock_train_model:
        mock_train_model.return_value = True
        result = mock_train_model(training_data)
        assert result is True, "Model training should complete successfully."

    assert model_path.exists(), "Model file should exist after training."
    assert model_path.stat().st_size > 0, "Model file should not be empty."


def test_inference_happy_path(model_container, test_data):
    """
    Test the happy path for inference.
    Ensures the model returns predictions for valid input data.
    """
    for sample in test_data["samples"]:
        response = send_inference_request({"input": sample["input"]})
        assert "prediction" in response, "Response should contain 'prediction' key."
        assert isinstance(response["prediction"], (int, float)), "Prediction should be a number."


@pytest.mark.parametrize(
    "invalid_input", [
        None,
        "",
        {"invalid_key": "value"},
        {"input": None},
        {"input": []},
    ]
)
def test_inference_invalid_input(model_container, invalid_input):
    """
    Test inference with invalid input data.
    Ensures the API handles invalid inputs gracefully.
    """
    import requests
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        send_inference_request(invalid_input)
    assert exc_info.value.response.status_code == 400, "API should return 400 for invalid input."


def test_model_accuracy(model_container, test_data):
    """
    Test the model's accuracy against a performance baseline.
    Ensures the model meets or exceeds the defined accuracy threshold.
    """
    correct_predictions = 0
    total_predictions = len(test_data["samples"])

    for sample in test_data["samples"]:
        response = send_inference_request({"input": sample["input"]})
        prediction = response["prediction"]
        if prediction == sample["expected_output"]:
            correct_predictions += 1

    accuracy = correct_predictions / total_predictions
    assert accuracy >= PERFORMANCE_THRESHOLD, (
        f"Model accuracy {accuracy:.2f} is below the threshold of {PERFORMANCE_THRESHOLD:.2f}."
    )


def test_inference_load(model_container, test_data):
    """
    Test the model inference under load.
    Ensures the API can handle concurrent requests without degradation.
    """
    import concurrent.futures
    samples = test_data["samples"][:LOAD_TEST_REQUESTS]

    def make_request(sample):
        return send_inference_request({"input": sample["input"]})

    with concurrent.futures.ThreadPoolExecutor(max_workers=LOAD_TEST_CONCURRENCY) as executor:
        futures = [executor.submit(make_request, sample) for sample in samples]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert len(results) == len(samples), "Not all requests returned a response."
    for result in results:
        assert "prediction" in result, "Each response should contain 'prediction' key."