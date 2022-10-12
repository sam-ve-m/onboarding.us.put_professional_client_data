from typing import Optional

from src.domain.enums.drive_wealth.employed_position import EmployedPosition
from src.domain.enums.drive_wealth.employed_status import EmployedStatus
from src.domain.enums.drive_wealth.employed_type import EmployedType
from src.domain.models.user_data.model import UserData


class EmployData(UserData):
    def __init__(
        self,
        unique_id: str,
        employ_status: EmployedStatus,
        employ_type: Optional[EmployedType],
        employ_position: Optional[EmployedPosition],
        employ_company_name: Optional[str],
    ):
        self.unique_id = unique_id
        self.employ_status = employ_status.value
        if employ_type:
            employ_type = employ_type.value
        self.employ_type = employ_type
        if employ_position:
            employ_position = employ_position.value
        self.employ_position = employ_position
        self.employ_company_name = employ_company_name

    def get_data_representation(self) -> dict:
        data = {
            "external_exchange_requirements.us.user_employ_status": self.employ_status,
            "external_exchange_requirements.us.user_employ_type": self.employ_type,
            "external_exchange_requirements.us.user_employ_position": self.employ_position,
            "external_exchange_requirements.us.user_employ_company_name": self.employ_company_name,
        }
        return data
