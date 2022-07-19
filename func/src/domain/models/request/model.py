from typing import Optional, Dict, Any

from pydantic import BaseModel, constr, root_validator

from src.domain.enums.drive_wealth.employed_position import EmployedPosition
from src.domain.enums.drive_wealth.employed_status import EmployedStatus
from src.domain.enums.drive_wealth.employed_type import EmployedType


class EmployForUs(BaseModel):
    user_employ_status: EmployedStatus
    user_employ_type: Optional[EmployedType]
    user_employ_position: Optional[EmployedPosition]
    user_employ_company_name: Optional[constr(min_length=1, max_length=100)]

    @root_validator()
    def validate_composition(cls, values: Dict[str, Any]):
        user_employ_status = values.get("user_employ_status")
        user_employ_type = values.get("user_employ_type")
        user_employ_position = values.get("user_employ_position")
        user_employ_company_name = values.get("user_employ_company_name")

        if user_employ_status in [
            EmployedStatus.EMPLOYED,
            EmployedStatus.SELF_EMPLOYED,
        ] and (
            user_employ_type is None
            or user_employ_position is None
            or user_employ_company_name is None
        ):
            raise ValueError(
                "You are EMPLOYED/SELF_EMPLOYED you must inform user_employ_type, user_employ_position and user_employ_company_name"
            )
        if user_employ_status not in [
            EmployedStatus.EMPLOYED,
            EmployedStatus.SELF_EMPLOYED,
        ]:
            values["user_employ_type"] = None
            values["user_employ_position"] = None
            values["user_employ_company_name"] = None
        return values
