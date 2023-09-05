import asyncio
import requests

from typing import Any, ClassVar, Dict, Mapping, Optional
from typing_extensions import Self

from viam.components.sensor import Sensor
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.registry import Registry, ResourceCreatorRegistration
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

# the rest url we wish to query
TOKEN_URL="https://api.ecobee.com/token"

class EcobeeApiSensor(Sensor):
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "ecobee-api"), "current")

    def __init__(self, name: str, api_key: str, refresh_token: str):
        self.api_key = api_key
        self.refresh_token = refresh_token

        self.update_token()
        super().__init__(name)

    def update_token(self):
        data = {"grant_type":"refresh_token", "code":self.refresh_token, "client_id":self.api_key}

        resp = requests.post(TOKEN_URL, data=data)

        self.access_token = resp.json()["access_token"]
        self.refresh_token = resp.json()["refresh_token"]
        return

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        # parse the args from the config and pass 'em into the constructor for later use.
        sensor = cls(config.name, config.attributes.fields["api_key"].string_value, config.attributes.fields["refresh_token"].string_value)
        return sensor

    async def get_readings(self, extra: Optional[Dict[str, Any]] = None, **kwargs) -> Mapping[str, Any]:
        # here we build up and submit a GET request
        thermostat_url = 'https://api.ecobee.com/1/thermostat?format=json&body={"selection":{"selectionType":"registered","selectionMatch":"","includeRuntime":true}}' 
        headers = {"Content-Type": "text/json", "Authorization": 'Bearer {}'.format(self.access_token)}

        response = requests.get(thermostat_url, headers = headers)

        # return the status code as an error if we dont get a 200 OK back.
        if response.status_code != 200:
            # likely a stale token, lets refresh
            self.update_token()
            return {"error": f"ecobee.com didn't return 200, instead got {response.status_code}. Refreshing token"}

        # this would be a great place to modify the data returned if the format direct from the API isn't to your liking.
        return response.json()


async def main():
    """This function creates and starts a new module, after adding all desired resource models.
    Resource creators must be registered to the resource registry before the module adds the resource model.
    """
    Registry.register_resource_creator(Sensor.SUBTYPE, EcobeeApiSensor.MODEL, ResourceCreatorRegistration(EcobeeApiSensor.new))

    module = Module.from_args()
    module.add_model_from_registry(Sensor.SUBTYPE, EcobeeApiSensor.MODEL)
    await module.start()


if __name__ == "__main__":
    asyncio.run(main())
