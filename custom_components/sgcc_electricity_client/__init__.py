from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN, CONFIG_NAME
from .utils.store import async_load_from_store
from .electricity import Electricity


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    data = await async_load_from_store(hass, CONFIG_NAME) or None
    addr = config_entry.data["addr"]
    session = async_create_clientsession(hass)
    hass.data[DOMAIN] = Electricity(hass, session, addr, data)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(config_entry, [Platform.SENSOR])
    )
    return True
