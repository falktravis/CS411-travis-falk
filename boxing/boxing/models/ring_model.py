import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    """
    A class to manage a ring of boxers.

    Attributes:
        ring (List[Song]): The list of boxers in the ring.

    """
    
    def __init__(self):
        """Initializes the RingModel with an empty ring.

        """
        self.ring: List[Boxer] = []

    def fight(self) -> str:
        """
        Simulates a fight between two boxers in the ring
        
        Returns:
            str: the name of the boxer that won the fight
        
        Raises:
            ValueError: if there are not 2 boxers in the ring
        
        """
        
        logger.info(f"Simulating fight between boxers in the ring")
    
        if len(self.ring) < 2:
            logger.error(f"There must be two boxers to start a fight.")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()
        
        logger.info(f"Determining winner based on skill")
        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1
        logger.info(f"Winner determined")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        
        logger.info(f"Successfully simulated fight between boxers in the ring. Winner: {winner.name}")
        return winner.name

    def clear_ring(self):
        """
        Clears all boxers from the ring.
        
        Clears all boxers from the ring. If the ring is already empty, logs a warning.
        """
        
        logger.info("Received request to clear the ring")
    
        if not self.ring:
            logger.warning("Clearing an empty ring")
            # raise ValueError("Playlist is empty")
            return
        self.ring.clear()
        
        logger.info("Successfully cleared the ring")

    def enter_ring(self, boxer: Boxer):
        """
        Adds a boxer to the ring.

        Args:
            boxer (Boxer): The boxer to add to the ring.

        Raises:
            TypeError: If the `boxer` is not a valid Boxer instance.
            ValueError: If the ring is full (already has 2 or more boxers)

        """
        
        logger.info("Received request for boxer to enter the ring")
        
        if not isinstance(boxer, Boxer):
            logger.error("Invalid type: boxer is not a valid Boxer instance")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.error(f"Ring is full and cannot add more boxers. Remove boxer or clear ring beforehand.")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)
        logger.info(f"Successfully added boxer to ring: {boxer.id} - {boxer.name} ({boxer.age})")

    def get_boxers(self) -> List[Boxer]:
        """
        Returns a list of all boxers in the ring.

        Returns:
            List[Boxer]: A list of all boxers in the ring.

        """
        
        if not self.ring:
            logger.warning("No boxers in the ring")
            return []
        else:
            pass
        
        logger.info("Retrieving all boxers in the ring")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """
        Calculates a fighting skill for a boxed. User to determine whether a boxer wins or loses a fight.
        
        Args:
            boxer (Boxer): the boxer to get the fighting skill for.

        Returns:
            int: A boxer's fighting skill calculated using their age, weight, name, and reach.
            
        """
        
        logger.info("Calculate boxer fighting skill")
        
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier
        
        logger.info("Successfully calculated boxer fighting skill")
        return skill
