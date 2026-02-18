import pytest
from unittest.mock import MagicMock, patch
from typing import List, Dict
from my_project.preprocessing import preprocess_data, validate_data, transform_data

# Constants for test data
VALID_INPUT_DATA = [
    {"id": 1, "name": "John Doe", "age": 30, "email": "john.doe@example.com"},
    {"id": 2, "name": "Jane Smith", "age": 25, "email": "jane.smith@example.com"},
]

INVALID_INPUT_DATA = [
    {"id": 1, "name": "", "age": -5, "email": "invalid-email"},
    {"id": None, "name": "Missing ID", "age": 40, "email": "missing.id@example.com"},
]

TRANSFORMED_DATA = [
    {"id": 1, "name": "JOHN DOE", "age": 30, "email": "john.doe@example.com"},
    {"id": 2, "name": "JANE SMITH", "age": 25, "email": "jane.smith@example.com"},
]

@pytest.fixture
def valid_data_fixture() -> List[Dict]:
    """Fixture for valid input data."""
    return VALID_INPUT_DATA

@pytest.fixture
def invalid_data_fixture() -> List[Dict]:
    """Fixture for invalid input data."""
    return INVALID_INPUT_DATA

@pytest.fixture
def mock_logger():
    """Fixture for mocking a logger."""
    with patch("my_project.preprocessing.logger") as mock_logger:
        yield mock_logger

@pytest.fixture
def mock_external_service():
    """Fixture for mocking an external service call."""
    with patch("my_project.preprocessing.external_service_call") as mock_service:
        mock_service.return_value = {"status": "success"}
        yield mock_service

def test_preprocess_data_happy_path(valid_data_fixture, mock_logger):
    """Test preprocess_data with valid input data."""
    result = preprocess_data(valid_data_fixture)
    assert result == TRANSFORMED_DATA, "Preprocessed data does not match expected output"
    mock_logger.info.assert_called_with("Data preprocessing completed successfully.")

def test_preprocess_data_invalid_input(invalid_data_fixture, mock_logger):
    """Test preprocess_data with invalid input data."""
    with pytest.raises(ValueError, match="Invalid data provided"):
        preprocess_data(invalid_data_fixture)
    mock_logger.error.assert_called_with("Data validation failed.")

@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        (VALID_INPUT_DATA, TRANSFORMED_DATA),
        ([{"id": 3, "name": "Alice", "age": 35, "email": "alice@example.com"}],
         [{"id": 3, "name": "ALICE", "age": 35, "email": "alice@example.com"}]),
    ],
)
def test_preprocess_data_parametrized(input_data, expected_output, mock_logger):
    """Parametrized test for preprocess_data with multiple scenarios."""
    result = preprocess_data(input_data)
    assert result == expected_output, "Preprocessed data does not match expected output"
    mock_logger.info.assert_called_with("Data preprocessing completed successfully.")

def test_validate_data_happy_path(valid_data_fixture):
    """Test validate_data with valid input data."""
    result = validate_data(valid_data_fixture)
    assert result is True, "Validation failed for valid input data"

def test_validate_data_invalid_input(invalid_data_fixture):
    """Test validate_data with invalid input data."""
    result = validate_data(invalid_data_fixture)
    assert result is False, "Validation passed for invalid input data"

def test_transform_data_happy_path(valid_data_fixture):
    """Test transform_data with valid input data."""
    result = transform_data(valid_data_fixture)
    assert result == TRANSFORMED_DATA, "Transformed data does not match expected output"

def test_transform_data_empty_input():
    """Test transform_data with empty input data."""
    result = transform_data([])
    assert result == [], "Transforming empty input should return an empty list"

def test_preprocess_data_external_service_call(valid_data_fixture, mock_external_service, mock_logger):
    """Test preprocess_data with an external service call."""
    result = preprocess_data(valid_data_fixture)
    mock_external_service.assert_called_once()
    assert result == TRANSFORMED_DATA, "Preprocessed data does not match expected output"
    mock_logger.info.assert_called_with("Data preprocessing completed successfully.")

def test_preprocess_data_performance(valid_data_fixture, mock_logger, benchmark):
    """Performance test for preprocess_data."""
    result = benchmark(preprocess_data, valid_data_fixture)
    assert result == TRANSFORMED_DATA, "Preprocessed data does not match expected output"
    mock_logger.info.assert_called_with("Data preprocessing completed successfully.")