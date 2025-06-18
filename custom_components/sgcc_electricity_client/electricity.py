import json
import asyncio
import traceback

from .utils.logger import LOGGER
from .const import CONFIG_NAME
from .utils.store import async_save_to_store

USER_LIST_URL = '{addr}/v1/electricity/user_list'
BALANCE_URL = '{addr}/v1/electricity/balance/{user_id}'
DAILYS_URL = '{addr}/v1/electricity/dailys/{user_id}'
LATEST_MONTH_URL = '{addr}/v1/electricity/latest_month/{user_id}'
THIS_YEAR_URL = '{addr}/v1/electricity/this_year/{user_id}'

class Electricity:
    def __init__(self, hass, session, addr, data=None):
        self._hass = hass
        self._session = session
        self._addr = addr
        self._user_list = []
        self._data = {} if data == None else data

    def get_user_list(self):
        return self._user_list
    
    def get_data(self):
        return self._data
    
    async def async_get_user_list(self):
        r = await self._session.get(USER_LIST_URL.format(addr=self._addr), timeout=10)
        result = []
        if r.status == 200:
            result = json.loads(await r.read())
        self._user_list = result
        return result

    async def async_get_balance(self, user_id):
        r = await self._session.get(BALANCE_URL.format(addr=self._addr, user_id=user_id), timeout=10)
        result = []
        if r.status == 200:
            result = json.loads(await r.read())
        self._data[user_id]["balance"] = result['balance']
        self._data[user_id]["refresh_time"] = result['updateTime']

    async def async_get_dailys(self, user_id):
        r = await self._session.get(DAILYS_URL.format(addr=self._addr, user_id=user_id), timeout=10)
        result = []
        if r.status == 200:
            result = json.loads(await r.read())
        self._data[user_id]["daily_ele_num"] = result["usage"]
        self._data[user_id]["daily_ele_cost"] = result["charge"]

    async def async_get_latest_month(self, user_id):
        r = await self._session.get(LATEST_MONTH_URL.format(addr=self._addr, user_id=user_id), timeout=10)
        result = []
        if r.status == 200:
            result = json.loads(await r.read())
        self._data[user_id]["last_month_ele_num"] = result["usage"]
        self._data[user_id]["last_month_ele_cost"] = result["charge"]
    
    async def async_get_this_year(self, user_id):
        r = await self._session.get(THIS_YEAR_URL.format(addr=self._addr, user_id=user_id), timeout=10)
        result = []
        if r.status == 200:
            result = json.loads(await r.read())
        self._data[user_id]["year_ele_num"] = result["usage"]
        self._data[user_id]["year_ele_cost"] = result["charge"]
    
    async def async_get_data(self):
        try:
            user_list = await self.async_get_user_list()
            LOGGER.debug(f"user_list: {user_list}")

            for user_id in user_list:
                if user_id not in self._data:
                    self._data[user_id] = {}
                tasks = [
                    self.async_get_balance(user_id),
                    self.async_get_dailys(user_id),
                    self.async_get_latest_month(user_id),
                    self.async_get_this_year(user_id)
                ]
                await asyncio.gather(*tasks)
            LOGGER.debug(f"Data {json.dumps(self._data)}")
            await async_save_to_store(self._hass,CONFIG_NAME,self._data)
        except Exception as err:
            traceback.print_exc()
            LOGGER.error(f"get data error :{err}")
        return self._data

    
