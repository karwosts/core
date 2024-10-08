"""Test Nice G.O. light."""

from unittest.mock import AsyncMock

from syrupy import SnapshotAssertion

from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.components.nice_go.const import DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration

from tests.common import MockConfigEntry, load_json_object_fixture, snapshot_platform


async def test_data(
    hass: HomeAssistant,
    mock_nice_go: AsyncMock,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that data gets parsed and returned appropriately."""

    await setup_integration(hass, mock_config_entry, [Platform.LIGHT])

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


async def test_turn_on(
    hass: HomeAssistant, mock_nice_go: AsyncMock, mock_config_entry: MockConfigEntry
) -> None:
    """Test that turning on the light works as intended."""

    await setup_integration(hass, mock_config_entry, [Platform.LIGHT])

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_garage_2_light"},
        blocking=True,
    )

    assert mock_nice_go.light_on.call_count == 1


async def test_turn_off(
    hass: HomeAssistant, mock_nice_go: AsyncMock, mock_config_entry: MockConfigEntry
) -> None:
    """Test that turning off the light works as intended."""

    await setup_integration(hass, mock_config_entry, [Platform.LIGHT])

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "light.test_garage_1_light"},
        blocking=True,
    )

    assert mock_nice_go.light_off.call_count == 1


async def test_update_light_state(
    hass: HomeAssistant,
    mock_nice_go: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that turning off the light works as intended."""

    await setup_integration(hass, mock_config_entry, [Platform.LIGHT])

    assert hass.states.get("light.test_garage_1_light").state == STATE_ON
    assert hass.states.get("light.test_garage_2_light").state == STATE_OFF

    device_update = load_json_object_fixture("device_state_update.json", DOMAIN)
    await mock_config_entry.runtime_data.on_data(device_update)
    device_update_1 = load_json_object_fixture("device_state_update_1.json", DOMAIN)
    await mock_config_entry.runtime_data.on_data(device_update_1)

    assert hass.states.get("light.test_garage_1_light").state == STATE_OFF
    assert hass.states.get("light.test_garage_2_light").state == STATE_ON
