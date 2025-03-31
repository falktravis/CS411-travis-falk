from dataclasses import asdict

import pytest

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


@pytest.fixture()
def ring_model():
    """Fixture to provide a new instance of RingModel for each test."""
    return RingModel()

"""Fixtures providing sample boxers for the tests."""
@pytest.fixture
def sample_boxer1():
    return Boxer(1, 'Boxer 1', 131, 68, 2.2, 25)

@pytest.fixture
def sample_boxer2():
    return Boxer(2, 'Boxer 2', 145, 71, 2.6, 32)

@pytest.fixture
def sample_ring(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]


##################################################
# Add / Remove Boxer Management Test Cases
##################################################


def test_enter_ring(ring_model, sample_boxer1):
    """Test adding a song to the playlist.

    """
    ring_model.enter_ring(sample_boxer1)
    assert len(ring_model.ring) == 0 or len(ring_model.ring) == 1
    assert ring_model.ring[0].name == 'Boxer 1'


def test_add_boxer_to_ring_too_many(ring_model, sample_boxer1):
    """Test error when adding a too many boxers to the ring by ID.

    """
    ring_model.enter_ring(sample_boxer1)
    with pytest.raises(ValueError, match="Ring is full, cannot add more boxers."):
        ring_model.enter_ring(sample_boxer1)
        ring_model.enter_ring(sample_boxer1)
        ring_model.enter_ring(sample_boxer1)


def test_add_boxer_to_ring_bad_boxer(ring_model, sample_boxer1):
    """Test error when adding a bad boxer to the ring.

    """
    with pytest.raises(TypeError, match="Invalid type: Expected 'Boxer', got 'dict'"):
        ring_model.enter_ring(asdict(sample_boxer1))


def test_clear_ring(ring_model, sample_boxer1):
    """Test clearing the entire ring.

    """
    ring_model.ring.append(sample_boxer1)

    ring_model.clear_ring()
    assert len(ring_model.ring) == 0, "Ring should be empty after clearing"


##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_boxers(ring_model, sample_ring):
    """Test successfully retrieving all boxers from the ring.

    """
    ring_model.ring.extend(sample_ring)
    
    all_boxers = ring_model.get_boxers()
    assert len(all_boxers) == 2

    assert all_boxers[0].id == 1
    assert all_boxers[0].name == 'Boxer 1'
    assert all_boxers[0].weight == 131
    assert all_boxers[0].height == 68
    assert all_boxers[0].reach == 2.2
    assert all_boxers[0].age == 25
    assert all_boxers[0].weight_class == 'FEATHERWEIGHT'
    
    assert all_boxers[1].id == 2
    assert all_boxers[1].name == 'Boxer 2'
    assert all_boxers[1].weight == 145
    assert all_boxers[1].height == 71
    assert all_boxers[1].reach == 2.6
    assert all_boxers[1].age == 32
    assert all_boxers[1].weight_class == 'LIGHTWEIGHT'
    
    
def test_get_fighting_skill(ring_model, sample_boxer1):
    """Test successfully retrieving a boxer's skill.
    
    """
    
    sample_boxer_skill1 = ring_model.get_fighting_skill(sample_boxer1)
    assert sample_boxer_skill1 == 917.22
    
    
def test_fight(ring_model, sample_ring, mocker):
    """Tests creating a fight between boxers in the ring."""
    
    ring_model.ring.extend(sample_ring)
    
    mock_stats_update = mocker.patch('boxing.models.ring_model.update_boxer_stats')
    result = ring_model.fight()
    assert result == 'Boxer 1'  # Ensure the fight method returns the winner
    
    ring_model.ring.clear() 
    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):
        ring_model.fight()
    
    
