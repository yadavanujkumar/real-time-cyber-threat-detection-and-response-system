import pytest
import requests
import time
from unittest.mock import patch
from typing import Dict, Any, Generator
from multiprocessing import Process
from psutil import cpu_percent, virtual_memory

# Constants
API_URL = "http://localhost:8000/inference"
TEST_PAYLOADS = [
    {"input": "test_data_1"},
    {"input": "test_data_2"},
    {"input": "test_data_3"},
]
MAX_LATENCY_MS = 500  # Maximum acceptable latency in milliseconds
MAX_CPU_USAGE = 80.0  # Maximum acceptable CPU usage percentage
MAX_MEMORY_USAGE = 80.0  # Maximum acceptable memory usage percentage
LOAD_TEST_CONCURRENCY = 50  # Number of concurrent requests for load testing
LOAD_TEST_DURATION = 30  # Duration of load test in seconds

@pytest.fixture(scope="module")
def setup_inference_api() -> Generator[None, None, None]:
    """
    Fixture to ensure the inference API is running before tests start.
    """
    # Here, you could add logic to start the API in a Docker container or verify its availability.
    # For simplicity, we assume the API is already running at API_URL.
    try:
        response = requests.get(f"{API_URL}/health")
        assert response.status_code == 200, "Inference API is not healthy or unavailable."
    except requests.ConnectionError:
        pytest.fail("Inference API is not running or accessible.")
    yield
    # Teardown logic if needed (e.g., stop Docker container)

@pytest.fixture
def mock_external_dependencies():
    """
    Fixture to mock external dependencies if needed.
    """
    with patch("requests.post") as mock_post:
        yield mock_post

def measure_resource_utilization(duration: int) -> Dict[str, Any]:
    """
    Measure CPU and memory usage over a given duration.
    """
    cpu_usage = []
    memory_usage = []
    start_time = time.time()

    while time.time() - start_time < duration:
        cpu_usage.append(cpu_percent(interval=1))
        memory_usage.append(virtual_memory().percent)

    return {
        "cpu": max(cpu_usage),
        "memory": max(memory_usage),
    }

@pytest.mark.parametrize("payload", TEST_PAYLOADS)
def test_inference_latency(setup_inference_api, payload):
    """
    Test that the inference API responds within the acceptable latency.
    """
    start_time = time.time()
    response = requests.post(API_URL, json=payload)
    end_time = time.time()

    assert response.status_code == 200, f"Expected 200, got {response.status_code}."
    latency = (end_time - start_time) * 1000  # Convert to milliseconds
    assert latency <= MAX_LATENCY_MS, f"Latency {latency}ms exceeds maximum {MAX_LATENCY_MS}ms."

def test_inference_error_handling(setup_inference_api):
    """
    Test that the inference API handles invalid input gracefully.
    """
    invalid_payload = {"invalid_key": "invalid_value"}
    response = requests.post(API_URL, json=invalid_payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code}."
    assert "error" in response.json(), "Error message not found in response."

@pytest.mark.parametrize("payload", TEST_PAYLOADS)
def test_inference_boundary_conditions(setup_inference_api, payload):
    """
    Test boundary conditions for the inference API.
    """
    # Example: Test with an empty input
    empty_payload = {"input": ""}
    response = requests.post(API_URL, json=empty_payload)

    assert response.status_code == 400, f"Expected 400, got {response.status_code}."
    assert "error" in response.json(), "Error message not found in response."

def test_inference_load_performance(setup_inference_api):
    """
    Load test the inference API to measure latency, throughput, and resource utilization.
    """
    def send_requests():
        for _ in range(LOAD_TEST_CONCURRENCY):
            requests.post(API_URL, json={"input": "load_test_data"})

    # Start resource monitoring in a separate process
    resource_monitor = Process(target=measure_resource_utilization, args=(LOAD_TEST_DURATION,))
    resource_monitor.start()

    # Start load test
    start_time = time.time()
    processes = [Process(target=send_requests) for _ in range(LOAD_TEST_CONCURRENCY)]
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    end_time = time.time()

    # Stop resource monitoring
    resource_monitor.terminate()
    resource_monitor.join()

    # Calculate throughput
    total_requests = LOAD_TEST_CONCURRENCY * LOAD_TEST_CONCURRENCY
    duration = end_time - start_time
    throughput = total_requests / duration

    # Assert throughput and resource utilization
    assert throughput > 0, "Throughput is unexpectedly low."
    resource_usage = measure_resource_utilization(LOAD_TEST_DURATION)
    assert resource_usage["cpu"] <= MAX_CPU_USAGE, f"CPU usage {resource_usage['cpu']}% exceeds maximum {MAX_CPU_USAGE}%."
    assert resource_usage["memory"] <= MAX_MEMORY_USAGE, f"Memory usage {resource_usage['memory']}% exceeds maximum {MAX_MEMORY_USAGE}%."

def test_integration_with_mocked_dependencies(mock_external_dependencies):
    """
    Test the inference API integration with mocked external dependencies.
    """
    mock_external_dependencies.return_value.status_code = 200
    mock_external_dependencies.return_value.json.return_value = {"result": "mocked_response"}

    payload = {"input": "test_data"}
    response = requests.post(API_URL, json=payload)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}."
    assert response.json()["result"] == "mocked_response", "Mocked response does not match expected value."