from decouple import config
from persephone_client import Persephone

from src.domain.enums.persephone_queue import PersephoneQueue
from src.domain.exceptions.model import InternalServerError, InvalidStepError
from src.domain.models.request.model import EmployRequest
from src.domain.models.user_data.device_info.model import DeviceInfo
from src.domain.models.user_data.employ.model import EmployData
from src.repositories.user.repository import UserRepository
from src.transport.user_step.transport import StepChecker


class EmployDataService:
    persephone_client = Persephone

    @staticmethod
    def __model_employ_data_to_persephone(
        employ_data: EmployData, device_info: DeviceInfo
    ) -> dict:
        data = {
            "unique_id": employ_data.unique_id,
            "employ_status": employ_data.employ_status,
            "employ_type": employ_data.employ_type,
            "employ_position": employ_data.employ_position,
            "employ_company_name": employ_data.employ_company_name,
            "device_info": device_info.device_info,
            "device_id": device_info.device_id,
        }
        return data

    @classmethod
    async def update_employ_for_us(cls, employ_request: EmployRequest):
        user_step = await StepChecker.get_onboarding_step(
            x_thebes_answer=employ_request.x_thebes_answer
        )
        if not user_step.is_in_correct_step():
            raise InvalidStepError(
                f"Step BR: {user_step.step_br} | Step US: {user_step.step_us}"
            )

        employ = employ_request.employ
        employ_data = EmployData(
            employ_request.unique_id,
            employ_status=employ.user_employ_status,
            employ_type=employ.user_employ_type,
            employ_position=employ.user_employ_position,
            employ_company_name=employ.user_employ_company_name,
        )

        (
            sent_to_persephone,
            status_sent_to_persephone,
        ) = await cls.persephone_client.send_to_persephone(
            topic=config("PERSEPHONE_TOPIC_USER"),
            partition=PersephoneQueue.USER_EMPLOY_US.value,
            message=cls.__model_employ_data_to_persephone(
                employ_data=employ_data,
                device_info=employ_request.device_info,
            ),
            schema_name="user_employ_form",
        )
        if sent_to_persephone is False:
            raise InternalServerError("Error sending data to Persephone")

        user_has_been_updated = await UserRepository.update_user(user_data=employ_data)
        if not user_has_been_updated:
            raise InternalServerError("Error updating user data")
