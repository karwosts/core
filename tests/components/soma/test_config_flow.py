"""Tests for the Soma config flow."""

from unittest.mock import patch

from api.soma_api import SomaApi
from requests import RequestException

from homeassistant.components.soma import DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry

MOCK_HOST = "123.45.67.89"
MOCK_PORT = 3000


async def test_form(hass: HomeAssistant) -> None:
    """Test user form showing."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM


async def test_import_abort(hass: HomeAssistant) -> None:
    """Test configuration from YAML aborting with existing entity."""
    MockConfigEntry(domain=DOMAIN).add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_IMPORT}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_setup"


async def test_import_create(hass: HomeAssistant) -> None:
    """Test configuration from YAML."""
    with patch.object(SomaApi, "list_devices", return_value={"result": "success"}):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={"host": MOCK_HOST, "port": MOCK_PORT},
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_error_status(hass: HomeAssistant) -> None:
    """Test Connect successfully returning error status."""
    with patch.object(SomaApi, "list_devices", return_value={"result": "error"}):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={"host": MOCK_HOST, "port": MOCK_PORT},
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "result_error"


async def test_key_error(hass: HomeAssistant) -> None:
    """Test Connect returning empty string."""

    with patch.object(SomaApi, "list_devices", return_value={}):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={"host": MOCK_HOST, "port": MOCK_PORT},
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "connection_error"


async def test_exception(hass: HomeAssistant) -> None:
    """Test if RequestException fires when no connection can be made."""
    with patch.object(SomaApi, "list_devices", side_effect=RequestException()):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={"host": MOCK_HOST, "port": MOCK_PORT},
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "connection_error"


async def test_full_flow(hass: HomeAssistant) -> None:
    """Check classic use case."""
    hass.data[DOMAIN] = {}
    with patch.object(SomaApi, "list_devices", return_value={"result": "success"}):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_USER},
            data={"host": MOCK_HOST, "port": MOCK_PORT},
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
