from typing import Optional

from src.domain.models.user_data.model import UserData


class EmployData(UserData):
    def __init__(
        self,
        unique_id: str,
        employ_status: str,
        employ_type: Optional[str],
        employ_position: Optional[str],
        employ_company_name: Optional[str],
    ):
        self.unique_id = unique_id
        self.employ_status = employ_status
        self.employ_type = employ_type
        self.employ_position = employ_position
        self.employ_company_name = employ_company_name

    def get_data_representation(self) -> dict:
        data = {
            "external_exchange_requirements.us.employ_status": self.employ_status,
            "external_exchange_requirements.us.employ_type": self.employ_type,
            "external_exchange_requirements.us.employ_position": self.employ_position,
            "external_exchange_requirements.us.employ_company_name": self.employ_company_name,
        }
        return data
