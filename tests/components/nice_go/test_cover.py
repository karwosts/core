"""Test Nice G.O. cover."""

from unittest.mock import AsyncMock

from freezegun.api import FrozenDateTimeFactory
from syrupy import SnapshotAssertion

from homeassistant.components.cover import (
    DOMAIN as COVER_DOMAIN,
    SERVICE_CLOSE_COVER,
    SERVICE_OPEN_COVER,
)
from homeassistant.components.nice_go.const import DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration

from tests.common import MockConfigEntry, load_json_object_fixture, snapshot_platform


async def test_covers(
    hass: HomeAssistant,
    mock_nice_go: AsyncMock,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that data gets parsed and returned appropriately."""

    await setup_integration(hass, mock_config_entry, [Platform.COVER])

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


async def test_open_cover(
    hass: HomeAssistant, mock_nice_go: AsyncMock, mock_config_entry: MockConfigEntry
) -> None:
    """Test that opening the cover works as intended."""

    await setup_integration(hass, mock_config_entry, [Platform.COVER])

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_OPEN_COVER,
        {ATTR_ENTITY_ID: "cover.test_garage_2"},
        blocking=True,
    )

    assert mock_nice_go.open_barrier.call_count == 0

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_OPEN_COVER,
        {ATTR_ENTITY_ID: "cover.test_garage_1"},
        blocking=True,
    )

    assert mock_nice_go.open_barrier.call_count == 1


async def test_close_cover(
    hass: HomeAssistant, mock_nice_go: AsyncMock, mock_config_entry: MockConfigEntry
) -> None:
    """Test that closing the cover works as intended."""

    await setup_integration(hass, mock_config_entry, [Platform.COVER])

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_CLOSE_COVER,
        {ATTR_ENTITY_ID: "cover.test_garage_1"},
        blocking=True,
    )

    assert mock_nice_go.close_barrier.call_count == 0

    await hass.services.async_call(
        COVER_DOMAIN,
        SERVICE_CLOSE_COVER,
        {ATTR_ENTITY_ID: "cover.test_garage_2"},
        blocking=True,
    )

    assert mock_nice_go.close_barrier.call_count == 1


async def test_update_cover_state(
    hass: HomeAssistant,
    mock_nice_go: AsyncMock,
    mock_config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test that closing the cover works as intended."""

    await setup_integration(hass, mock_config_entry, [Platform.COVER])

    assert hass.states.get("cover.test_garage_1").state == STATE_CLOSED
    assert hass.states.get("cover.test_garage_2").state == STATE_OPEN

    device_update = load_json_object_fixture("device_state_update.json", DOMAIN)
    await mock_config_entry.runtime_data.on_data(device_update)
    device_update_1 = load_json_object_fixture("device_state_update_1.json", DOMAIN)
    await mock_config_entry.runtime_data.on_data(device_update_1)

    assert hass.states.get("cover.test_garage_1").state == STATE_OPENING
    assert hass.states.get("cover.test_garage_2").state == STATE_CLOSING
