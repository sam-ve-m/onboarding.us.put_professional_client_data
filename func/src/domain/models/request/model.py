from typing import Optional, Dict, Any

from pydantic import BaseModel, constr, root_validator

from func.src.domain.enums.drive_wealth.employed_position import EmployedPosition
from func.src.domain.enums.drive_wealth.employed_status import EmployedStatus
from func.src.domain.enums.drive_wealth.employed_type import EmployedType
from func.src.domain.models.jwt_data.model import Jwt
from func.src.domain.models.user_data.device_info.model import DeviceInfo
from func.src.transport.device_info.transport import DeviceSecurity


class EmployForUs(BaseModel):
    user_employ_status: EmployedStatus
    user_employ_type: Optional[EmployedType]
    user_employ_position: Optional[EmployedPosition]
    user_employ_company_name: Optional[constr(min_length=1, max_length=100)]

    @root_validator()
    def validate_composition(cls, values: Dict[str, Any]):
        user_employ_status = values.get("employ_status")
        user_employ_type = values.get("employ_type")
        user_employ_position = values.get("employ_position")
        user_employ_company_name = values.get("employ_company_name")

        if user_employ_status in [
            EmployedStatus.EMPLOYED,
            EmployedStatus.SELF_EMPLOYED,
        ] and (
            user_employ_type is None
            or user_employ_position is None
            or user_employ_company_name is None
        ):
            raise ValueError(
                "You are EMPLOYED/SELF_EMPLOYED you must inform employ_type, employ_position and employ_company_name"
            )
        if user_employ_status not in [
            EmployedStatus.EMPLOYED,
            EmployedStatus.SELF_EMPLOYED,
        ]:
            values["employ_type"] = None
            values["employ_position"] = None
            values["employ_company_name"] = None
        return values


class EmployRequest:
    def __init__(
        self,
        x_thebes_answer: str,
        device_info: DeviceInfo,
        unique_id: str,
        employ: EmployForUs,
    ):
        self.x_thebes_answer = x_thebes_answer
        self.device_info = device_info
        self.unique_id = unique_id
        self.employ = employ

    @classmethod
    async def build(cls, x_thebes_answer: str, x_device_info: str, parameters: dict):
        employ = EmployForUs(**parameters)
        jwt = await Jwt.build(jwt=x_thebes_answer)
        device_info = await DeviceSecurity.get_device_info(x_device_info)
        return cls(
            x_thebes_answer=x_thebes_answer,
            device_info=device_info,
            unique_id=jwt.unique_id,
            employ=employ,
        )
