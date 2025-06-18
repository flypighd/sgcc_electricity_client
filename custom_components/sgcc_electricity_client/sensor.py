from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

import datetime

from .const import DOMAIN, VERSION
from .electricity import Electricity
from .coordinator import ElectricityCoordinator

UNIT_YUAN = "元"

ENTITY_ID_SENSOR_FORMAT = SENSOR_DOMAIN + ".sgcc_electricity_"

SENSOR_TYPES = [
    {
        "key":"balance",
        "name": "账户余额",
        "native_unit_of_measurement": UNIT_YUAN,
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL
    },
    {
        "key": "year_ele_num",
        "name": "年度累计用电",
        "native_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL
    },
    {
        "key": "year_ele_cost",
        "name": "年度累计电费",
        "native_unit_of_measurement": UNIT_YUAN,
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL
    },
    {
        "key": "last_month_ele_num",
        "name": "上个月用电",
        "native_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL
    },
    {
        "key": "last_month_ele_cost",
        "name": "上个月电费",
        "native_unit_of_measurement": UNIT_YUAN,
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL
    },
        {
        "key": "daily_ele_num",
        "name": "每日用电量",
        "native_unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL
    },
    {
        "key": "daily_ele_cost",
        "name": "每日电费",
        "native_unit_of_measurement": UNIT_YUAN,
        "device_class": SensorDeviceClass.MONETARY,
        "state_class": SensorStateClass.TOTAL
    },
    {
        "key": "refresh_time",
        "name": "最近刷新时间"
    }
]

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = ElectricityCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    
    for user_id in coordinator.data.keys():
        async_add_entities(
            [ElectricitySensor(user_id, sensor_type, entry.entry_id, coordinator) for sensor_type in SENSOR_TYPES]
        )

class ElectricitySensor(CoordinatorEntity[ElectricityCoordinator], SensorEntity):

    _attr_has_entity_name = True

    def __init__(
        self, user_id, sensor_type, entry_id: str, coordinator: ElectricityCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self.user_id = user_id
        self.sensor_type = sensor_type
        self.entity_id = SENSOR_DOMAIN + ".electricity" + "_" + user_id + "_" + sensor_type["key"]
        self._attr_name = sensor_type["name"]
        self._attr_unique_id = entry_id + "-" + user_id + "-" + sensor_type["key"]


        if "device_class" in sensor_type:
            self._attr_device_class = sensor_type["device_class"]

        if "state_class" in sensor_type:
            self._attr_state_class = sensor_type["state_class"]

        if "native_unit_of_measurement" in sensor_type:
            self._attr_native_unit_of_measurement = sensor_type["native_unit_of_measurement"]

        self._attr_device_info = {
            "name": user_id,
            "identifiers": {(DOMAIN, user_id)},
            "sw_version": VERSION,
            "manufacturer": "Javed",
            "model": "户号：" + user_id
        }

    @property
    def native_value(self):
        data = self.coordinator.data[self.user_id]
        return data[self.sensor_type["key"]]
    
