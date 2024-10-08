"""Test ViCare migration."""

from unittest.mock import patch

from homeassistant.components.vicare.const import DOMAIN
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from . import MODULE
from .conftest import Fixture, MockPyViCare

from tests.common import MockConfigEntry


# Device migration test can be removed in 2025.4.0
async def test_device_migration(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that the device registry is updated correctly."""
    fixtures: list[Fixture] = [Fixture({"type:boiler"}, "vicare/Vitodens300W.json")]
    with (
        patch(f"{MODULE}.vicare_login", return_value=MockPyViCare(fixtures)),
        patch(f"{MODULE}.PLATFORMS", [Platform.CLIMATE]),
    ):
        mock_config_entry.add_to_hass(hass)

        device_registry.async_get_or_create(
            config_entry_id=mock_config_entry.entry_id,
            identifiers={
                (DOMAIN, "gateway0"),
            },
        )

        await hass.config_entries.async_setup(mock_config_entry.entry_id)

        await hass.async_block_till_done()

    assert device_registry.async_get_device(identifiers={(DOMAIN, "gateway0")}) is None

    assert (
        device_registry.async_get_device(
            identifiers={(DOMAIN, "gateway0_deviceSerialVitodens300W")}
        )
        is not None
    )


# Entity migration test can be removed in 2025.4.0
async def test_climate_entity_migration(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that the climate entity unique_id gets migrated correctly."""
    fixtures: list[Fixture] = [Fixture({"type:boiler"}, "vicare/Vitodens300W.json")]
    with (
        patch(f"{MODULE}.vicare_login", return_value=MockPyViCare(fixtures)),
        patch(f"{MODULE}.PLATFORMS", [Platform.CLIMATE]),
    ):
        mock_config_entry.add_to_hass(hass)

        entry1 = entity_registry.async_get_or_create(
            domain=Platform.CLIMATE,
            platform=DOMAIN,
            config_entry=mock_config_entry,
            unique_id="gateway0-0",
            translation_key="heating",
        )
        entry2 = entity_registry.async_get_or_create(
            domain=Platform.CLIMATE,
            platform=DOMAIN,
            config_entry=mock_config_entry,
            unique_id="gateway0_deviceSerialVitodens300W-heating-1",
            translation_key="heating",
        )
        entry3 = entity_registry.async_get_or_create(
            domain=Platform.CLIMATE,
            platform=DOMAIN,
            config_entry=mock_config_entry,
            unique_id="gateway1-0",
            translation_key="heating",
        )

        await hass.config_entries.async_setup(mock_config_entry.entry_id)

        await hass.async_block_till_done()

    assert (
        entity_registry.async_get(entry1.entity_id).unique_id
        == "gateway0_deviceSerialVitodens300W-heating-0"
    )
    assert (
        entity_registry.async_get(entry2.entity_id).unique_id
        == "gateway0_deviceSerialVitodens300W-heating-1"
    )
    assert entity_registry.async_get(entry3.entity_id).unique_id == "gateway1-0"
