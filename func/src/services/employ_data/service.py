from decouple import config
from persephone_client import Persephone

from src.domain.enums.persephone_queue import PersephoneQueue
from src.domain.exceptions.model import InternalServerError
from src.domain.models.request.model import EmployForUs
from src.repositories.step_validator.repository import StepValidator
from src.repositories.user.repository import UserRepository


class EmployDataService:
    persephone_client = Persephone

    @staticmethod
    def __model_employ_data_to_persephone(
        employ_status: str,
        employ_type: str,
        employ_position: str,
        employ_company_name: str,
        unique_id: str,
    ) -> dict:
        data = {
            "unique_id": unique_id,
            "employ_status": employ_status,
            "employ_type": employ_type,
            "employ_position": employ_position,
            "employ_company_name": employ_company_name,
        }
        return data

    @classmethod
    async def update_employ_for_us(
        cls, employ_data: EmployForUs, payload: dict
    ) -> None:

        await StepValidator.validate_onboarding_step(
            x_thebes_answer=payload["x_thebes_answer"]
        )

        unique_id = payload["data"]["user"]["unique_id"]

        user_employ_status = employ_data.user_employ_status.value
        user_employ_type = employ_data.user_employ_type.value
        user_employ_position = employ_data.user_employ_position.value
        user_employ_company_name = employ_data.user_employ_company_name

        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_TAX_RESIDENCE_CONFIRMATION_US.value,
            message=cls.__model_employ_data_to_persephone(
                employ_status=user_employ_status,
                employ_type=user_employ_type,
                employ_position=user_employ_position,
                employ_company_name=user_employ_company_name,
                unique_id=unique_id,
            ),
            schema_name="user_employ_form",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

        was_updated = await UserRepository.update_user(
            unique_id=unique_id,
            new={
                "external_exchange_requirements.us.user_employ_status": user_employ_status,
                "external_exchange_requirements.us.user_employ_type": user_employ_type,
                "external_exchange_requirements.us.user_employ_position": user_employ_position,
                "external_exchange_requirements.us.user_employ_company_name": user_employ_company_name,
            },
        )
        if not was_updated:
            raise InternalServerError("Error updating user data")
