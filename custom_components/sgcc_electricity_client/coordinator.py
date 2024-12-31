from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .electricity import Electricity

from .const import DOMAIN
from .utils.logger import LOGGER

class ElectricityCoordinator(DataUpdateCoordinator):

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=300)
        )
        self.first_setup = True
        self.electricity: Electricity = hass.data[DOMAIN]

    async def _async_update_data(self):
        await self.electricity.async_get_data()
        self.first_setup = False
        return self.electricity.get_data()