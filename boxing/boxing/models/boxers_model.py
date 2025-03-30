from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    """
    A class to store information about a boxer.

    Attributes:
        id (int): boxer identification number
        name (str): boxer's name (unique)
        weight (int): weight of the boxer in pounds
        height (int): height of the boxer in inches
        reach (float): how far the boxer can reach
        age (int): how old the boxer is in years
        weight_class (str): a class of weight based on the boxer weight attribute
    """
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        """Initializes the Boxer's weight class directly after class initialization.

        """
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """
    Creates a boxer in the database

    Args:
        name (str): name of the boxer to create
        weight (int): weight of the boxer to create in pounds
        height (int): height of the boxer to create in inches
        reach (float): arm reach of the boxer to create
        age (int): how old the boxer to create is in years

    Raises:
        ValueError: if `weight` less than 125
            if `height` less than or equal to 0
            if `reach` less than or equal to 0
            if `age` not between or equal to 18 through 40
            if `name` already exists in the database
        sqlite3.IntegrityError: if `name` already exists in the database
        sqlite3.Error: if SQLite produces extraneous error
    
    """
    logger.info(f"Received request to create boxer: {name}, weight: {weight}, height: {height}, reach: {reach}, age: {age}")
    
    if weight < 125:
        logger.error(f"Invalid weight: {weight}. Must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.error(f"Invalid height: {height}. Must be greater than 0.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.error(f"Invalid reach: {reach}. Must be greater than 0.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.error(f"Invalid age: {age}. Must be between 18 and 40.")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.error(f"Boxer with name '{name}' already exists")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))

            conn.commit()
            logger.info(f"Successfully created boxer: {name} with weight class {get_weight_class(weight)}")

    except sqlite3.IntegrityError:
        logger.error(f"Boxer with name '{name}' already exists")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Error creating boxer: {str(e)}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """
    Deletes a boxer from the database.

    Args:
        boxer_id (int): id of the boxer to delete from the database

    Raises:
        ValueError: if boxer is not found within the database
        sqlite3.Error: if SQLite produces extraneous error
    
    """
    logger.info(f"Received request to delete boxer with ID {boxer_id}")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()
            logger.info(f"Successfully deleted boxer with ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Error deleting boxer: {str(e)}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]:
    """
    Gets a sorted list of the boxers

    Args:
        sort_by (str): the attribute of the boxer to sort the leaderboard by. Defaults to "wins"

    Returns:
        List[dict[str, Any]]: sorted list of boxers stored as dictionaries. sorted by `sort_by`.

    Raises:
        ValueError: if `sort_by` is not equal to win_pct or wins
        sqlite3.Error: if SQLite produces extraneous error
    
    """
    logger.info(f"Retrieving leaderboard sorted by {sort_by}")
    
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sort_by parameter: {sort_by}")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row['id'],
                'name': row['name'],
                'weight': row['weight'],
                'height': row['height'],
                'reach': row['reach'],
                'age': row['age'],
                #'weight_class': get_weight_class(row['weight']),  # Calculate weight class
                'fights': row['fights'],
                'wins': row['wins'],
                'win_pct': round(row['win_pct'] * 1.0, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        logger.info(f"Successfully retrieved leaderboard: {len(leaderboard)} boxers returned")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Error retrieving leaderboard: {str(e)}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """
    Gets a boxer from the database using their unique id.

    Args:
        boxer_id (int): the id of the boxer to be obtained from the database.

    Returns:
        Boxer: the boxer class with the id specified by `boxer_id`.

    Raises:
        ValueError: if the boxer with id `boxer_id` is not found in the database
        sqlite3.Error: if SQLite produces extraneous error
    
    """
    logger.info(f"Retrieving boxer with ID {boxer_id}")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully retrieved boxer: {boxer.name} (ID: {boxer.id})")
                return boxer
            else:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Error retrieving boxer by ID: {str(e)}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """
    Gets a boxer from the database using their unique name.

    Args:
        boxer_name (str): the name of the boxer to be obtained from the database.

    Returns:
        Boxer: the boxer class with the name specified by `boxer_name`.

    Raises:
        ValueError: if the boxer with name `boxer_name` is not found in the database
        sqlite3.Error: if SQLite produces extraneous error
    
    """
    logger.info(f"Retrieving boxer with name '{boxer_name}'")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Successfully retrieved boxer: {boxer.name} (ID: {boxer.id})")
                return boxer
            else:
                logger.error(f"Boxer '{boxer_name}' not found.")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Error retrieving boxer by name: {str(e)}")
        raise e


def get_weight_class(weight: int) -> str:
    """
    Gets the weight class of any given boxer using their specified weight

    Args:
        weight (int): the boxer's weight in pounds

    Returns:
        'FEATHERWEIGHT' if `weight` is greater than or equal to 125 and less than 133
        'LIGHTWEIGHT' if `weight` is greater than or equal to 133 and less than 166
        'MIDDLEWEIGHT' if `weight` is greater than or equal to 166 and less than 203
        'HEAVYWEIGHT' if `weight` is greater than or equal to 203

    Raises:
        ValueError: if `weight` is less than 125
    
    """
    logger.info(f"Determining weight class for weight: {weight} pounds")
    
    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}. Weight must be at least 125.")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")

    logger.info(f"Weight class determined: {weight_class}")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """
    Updates the stats of a boxer based on a win or loss in a fight

    Args:
        boxer_id (int): the id of the boxer that won or lost a fight
        result (str): whether or not the boxer won the fight

    Raises:
        ValueError: if `result` is not equal to 'win' or 'loss'
            if the boxer with id `boxer_id` is not found in the database
        sqlite3.Error: if SQLite produces extraneous error
    
    """
    logger.info(f"Received request to update boxer ID {boxer_id} stats with result: {result}")
    
    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
                logger.info(f"Updated boxer ID {boxer_id} with a win")
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))
                logger.info(f"Updated boxer ID {boxer_id} with a loss")

            conn.commit()
            logger.info(f"Successfully updated stats for boxer ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Error updating boxer stats: {str(e)}")
        raise e
