"""Config flow for bjwater integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
import re

from homeassistant.helpers.aiohttp_client import async_create_clientsession, async_get_clientsession

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigType, ConfigEntry

from .const import DOMAIN
from requests import RequestException
from .utils.logger import LOGGER
from .electricity import Electricity


STEP_ADDR_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("addr"): str
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    addr = data["addr"]
    pattern = r'https?://([^/]+)?:(\d+)?'
    match = re.match(pattern, addr)
    if match:
        electricity = Electricity(hass, session, addr, None)
        try:
            user_list = await electricity.async_get_user_list()
            if len(user_list) == 0:
                raise NoUser
        except RequestException:
            raise CannotConnect
    else:
        raise InvalidFormat
    # Return info that you want to store in the config entry.
    return {"title": "服务器地址：" + addr}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for bjwater."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entries = self.hass.config_entries.async_entries(DOMAIN)
            if len(entries) > 0:
                for entity in entries:
                    user_code = entity.data["addr"]
                    if user_input["addr"] == user_code:
                        return self.async_abort(reason="already_configured")
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except NoUser:
                errors["base"] = "no_user"
            except InvalidFormat:
                errors["base"] = "invalid_format"
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)
        return self.async_show_form(step_id="user", data_schema=STEP_ADDR_DATA_SCHEMA, errors=errors)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class NoUser(HomeAssistantError):
    """Error to indicate there is invalid auth."""

class InvalidFormat(HomeAssistantError):
    """Error to indicate there is invalid format."""