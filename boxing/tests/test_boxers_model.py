from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    """Normalize whitespace in SQL queries for comparison."""
    return re.sub(r'\s+', ' ', sql_query).strip()


# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxers_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Boxer Creation and Deletion Tests
#
######################################################

def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the database."""
    create_boxer(name="Mike Tyson", weight=220, height=71, reach=71.0, age=25)
    
    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Mike Tyson", 220, 71, 71.0, 25)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_boxer_invalid_weight():
    """Test error when trying to create a boxer with an invalid weight."""
    with pytest.raises(ValueError, match="Invalid weight: 124. Must be at least 125."):
        create_boxer(name="Tiny Boxer", weight=124, height=65, reach=64.0, age=25)


def test_create_boxer_invalid_height():
    """Test error when trying to create a boxer with an invalid height."""
    with pytest.raises(ValueError, match="Invalid height: 0. Must be greater than 0."):
        create_boxer(name="Zero Height Boxer", weight=180, height=0, reach=70.0, age=25)


def test_create_boxer_invalid_reach():
    """Test error when trying to create a boxer with an invalid reach."""
    with pytest.raises(ValueError, match="Invalid reach: 0. Must be greater than 0."):
        create_boxer(name="Zero Reach Boxer", weight=180, height=70, reach=0, age=25)


def test_create_boxer_invalid_age():
    """Test error when trying to create a boxer with an invalid age."""
    with pytest.raises(ValueError, match="Invalid age: 17. Must be between 18 and 40."):
        create_boxer(name="Young Boxer", weight=180, height=70, reach=70.0, age=17)

    with pytest.raises(ValueError, match="Invalid age: 41. Must be between 18 and 40."):
        create_boxer(name="Old Boxer", weight=180, height=70, reach=70.0, age=41)


def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name (should raise an error)."""
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")
    
    with pytest.raises(ValueError, match="Boxer with name 'Mike Tyson' already exists"):
        create_boxer(name="Mike Tyson", weight=220, height=71, reach=71.0, age=25)


def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the database by boxer ID."""
    # Simulate the existence of a boxer with id=1
    mock_cursor.fetchone.return_value = (True,)
    
    delete_boxer(1)
    
    # Check the verification query
    expected_select_query = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    actual_select_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    
    assert actual_select_query == expected_select_query, "The SELECT query did not match the expected structure."
    
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    expected_select_args = (1,)
    
    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    
    # Check the delete query
    expected_delete_query = normalize_whitespace("DELETE FROM boxers WHERE id = ?")
    actual_delete_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_delete_query == expected_delete_query, "The DELETE query did not match the expected structure."
    
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]
    expected_delete_args = (1,)
    
    assert actual_delete_args == expected_delete_args, f"The DELETE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


def test_delete_boxer_not_found(mock_cursor):
    """Test error when trying to delete a non-existent boxer."""
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Boxer Retrieval Tests
#
######################################################

def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by ID."""
    mock_cursor.fetchone.return_value = (1, "Mike Tyson", 220, 71, 71.0, 25, 10, 8)
    
    result = get_boxer_by_id(1)
    
    expected_result = Boxer(1, "Mike Tyson", 220, 71, 71.0, 25)
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_not_found(mock_cursor):
    """Test error when getting a non-existent boxer by ID."""
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)
        
    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (999,)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name."""
    mock_cursor.fetchone.return_value = (1, "Mike Tyson", 220, 71, 71.0, 25, 10, 8)
    
    result = get_boxer_by_name("Mike Tyson")
    
    expected_result = Boxer(1, "Mike Tyson", 220, 71, 71.0, 25)
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Mike Tyson",)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_name_not_found(mock_cursor):
    """Test error when getting a non-existent boxer by name."""
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer 'Nonexistent Boxer' not found."):
        get_boxer_by_name("Nonexistent Boxer")
        
    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Nonexistent Boxer",)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


######################################################
#
#    Weight Class Tests
#
######################################################

def test_get_weight_class_featherweight():
    """Test determining featherweight class."""
    result = get_weight_class(125)
    expected_result = "FEATHERWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    result = get_weight_class(132)
    expected_result = "FEATHERWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_weight_class_lightweight():
    """Test determining lightweight class."""
    result = get_weight_class(133)
    expected_result = "LIGHTWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    result = get_weight_class(165)
    expected_result = "LIGHTWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_weight_class_middleweight():
    """Test determining middleweight class."""
    result = get_weight_class(166)
    expected_result = "MIDDLEWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    result = get_weight_class(202)
    expected_result = "MIDDLEWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_weight_class_heavyweight():
    """Test determining heavyweight class."""
    result = get_weight_class(203)
    expected_result = "HEAVYWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    result = get_weight_class(250)
    expected_result = "HEAVYWEIGHT"
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_weight_class_invalid_weight():
    """Test error for invalid weight."""
    with pytest.raises(ValueError, match="Invalid weight: 124. Weight must be at least 125."):
        get_weight_class(124)


######################################################
#
#    Leaderboard Tests
#
######################################################

def test_get_leaderboard_by_wins(mock_cursor):
    """Test getting the leaderboard sorted by wins."""
    mock_boxers = [
        {"id": 1, "name": "Mike Tyson", "weight": 220, "height": 71, "reach": 71.0, "age": 25, "fights": 10, "wins": 8, "win_pct": 0.8},
        {"id": 2, "name": "Floyd Mayweather", "weight": 150, "height": 68, "reach": 72.0, "age": 30, "fights": 12, "wins": 12, "win_pct": 1.0}
    ]
    mock_cursor.fetchall.return_value = mock_boxers
    
    result = get_leaderboard()
    
    expected_result = mock_boxers
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_by_win_pct(mock_cursor):
    """Test getting the leaderboard sorted by win percentage."""
    mock_boxers = [
        {"id": 2, "name": "Floyd Mayweather", "weight": 150, "height": 68, "reach": 72.0, "age": 30, "fights": 12, "wins": 12, "win_pct": 1.0},
        {"id": 1, "name": "Mike Tyson", "weight": 220, "height": 71, "reach": 71.0, "age": 25, "fights": 10, "wins": 8, "win_pct": 0.8}
    ]
    mock_cursor.fetchall.return_value = mock_boxers
    
    result = get_leaderboard("win_pct")
    
    expected_result = mock_boxers
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY win_pct DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_invalid_sort(mock_cursor):
    """Test error when providing an invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        get_leaderboard("invalid_sort")


def test_get_leaderboard_empty(mock_cursor):
    """Test getting an empty leaderboard."""
    mock_cursor.fetchall.return_value = []
    
    result = get_leaderboard("wins")
    
    expected_result = []
    
    assert result == expected_result, f"Expected {expected_result}, got {result}"
    
    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SQL query did not match the expected structure."


######################################################
#
#    Stats Update Tests
#
######################################################

def test_update_boxer_stats_win(mock_cursor):
    """Test updating a boxer's stats with a win."""
    # Simulate that a boxer exists with the given ID
    mock_cursor.fetchone.return_value = (1, "Mike Tyson", 220, 71, 71.0, 25, 10, 8)
    
    update_boxer_stats(1, "win")
    
    # Check that the right SQL queries were executed
    assert len(mock_cursor.execute.call_args_list) == 2, "Expected two SQL queries to be executed"
    
    # Check the select query
    expected_select_query = normalize_whitespace("""
        SELECT id
        FROM boxers WHERE id = ?
    """)
    actual_select_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    
    assert actual_select_query == expected_select_query, "The SELECT query did not match the expected structure."
    
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    expected_select_args = (1,)
    
    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    
    # Check the update query
    expected_update_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?
    """)
    actual_update_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_update_query == expected_update_query, "The UPDATE query did not match the expected structure."
    
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]
    expected_update_args = (1,)
    
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_update_boxer_stats_loss(mock_cursor):
    """Test updating a boxer's stats with a loss."""
    # Simulate that a boxer exists with the given ID
    mock_cursor.fetchone.return_value = (1, "Mike Tyson", 220, 71, 71.0, 25, 10, 8)
    
    update_boxer_stats(1, "loss")
    
    # Check that the right SQL queries were executed
    assert len(mock_cursor.execute.call_args_list) == 2, "Expected two SQL queries to be executed"
    
    # Check the select query
    expected_select_query = normalize_whitespace("""
        SELECT id
        FROM boxers WHERE id = ?
    """)
    actual_select_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    
    assert actual_select_query == expected_select_query, "The SELECT query did not match the expected structure."
    
    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    expected_select_args = (1,)
    
    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    
    # Check the update query
    expected_update_query = normalize_whitespace("""
        UPDATE boxers SET fights = fights + 1 WHERE id = ?
    """)
    actual_update_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    
    assert actual_update_query == expected_update_query, "The UPDATE query did not match the expected structure."
    
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]
    expected_update_args = (1,)
    
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_update_boxer_stats_invalid_result():
    """Test error when providing an invalid result."""
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_boxer_stats(1, "draw")


def test_update_boxer_stats_not_found(mock_cursor):
    """Test error when updating stats of a non-existent boxer."""
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Boxer with ID 999 not found."):
        update_boxer_stats(999, "win")
        
    expected_query = normalize_whitespace("""
        SELECT id
        FROM boxers WHERE id = ?
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    
    assert actual_query == expected_query, "The SELECT query did not match the expected structure."
    
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (999,)
    
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    
    
    
