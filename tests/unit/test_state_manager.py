"""Tests for StateManager."""
import pytest
from unittest.mock import MagicMock

from mynewapp.core.state_manager import StateManager


@pytest.fixture
def state(qapp):
    return StateManager()


def test_initial_step_is_zero(state):
    assert state.current_step == 0


def test_next_step_increments(state):
    state.next_step()
    assert state.current_step == 1


def test_prev_step_does_not_go_below_zero(state):
    state.prev_step()
    assert state.current_step == 0


def test_is_first_step(state):
    assert state.is_first_step() is True


def test_is_last_step(state):
    state.go_to_step(state.total_steps - 1)
    assert state.is_last_step() is True


def test_update_config_emits_signal(state):
    received = []
    state.config_changed.connect(lambda c: received.append(c))
    state.update_config(name="new-name")
    assert len(received) == 1
    assert received[0].name == "new-name"


def test_update_nested_config(state):
    state.update_nested("ai_tools", enabled=True)
    assert state.config.ai_tools.enabled is True
