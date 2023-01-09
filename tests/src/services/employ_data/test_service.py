from unittest.mock import patch

import pytest
from persephone_client import Persephone
from decouple import Config

with patch.object(Config, "__call__"):
    from func.src.domain.exceptions.model import InternalServerError, InvalidStepError
    from func.src.domain.models.request.model import EmployForUs, EmployRequest
    from func.src.domain.models.user_data.device_info.model import DeviceInfo
    from func.src.domain.models.user_data.employ.model import EmployData
    from func.src.domain.models.user_data.onboarding_step.model import UserOnboardingStep
    from func.src.repositories.user.repository import UserRepository
    from func.src.services.employ_data.service import EmployDataService
    from func.src.transport.user_step.transport import StepChecker

employ_model_dummy = EmployForUs(
    **{
        "user_employ_status": "EMPLOYED",
        "user_employ_type": "UTILITIES",
        "user_employ_position": "ADMINISTRATOR",
        "user_employ_company_name": "CAESAR Inc.",
    }
)
stub_device_info = DeviceInfo({"precision": 1}, "")
company_director_request_dummy = EmployRequest(
    x_thebes_answer="x_thebes_answer",
    unique_id="unique_id",
    employ=employ_model_dummy,
    device_info=stub_device_info,
)
company_director_data_dummy = EmployData(
    unique_id=company_director_request_dummy.unique_id,
    employ_status=employ_model_dummy.user_employ_status,
    employ_type=employ_model_dummy.user_employ_type,
    employ_position=employ_model_dummy.user_employ_position,
    employ_company_name=employ_model_dummy.user_employ_company_name,
)
onboarding_step_correct_stub = UserOnboardingStep("finished", "employ")
onboarding_step_incorrect_stub = UserOnboardingStep("finished", "some_step")


def test___model_company_director_data_to_persephone():
    result = EmployDataService._EmployDataService__model_employ_data_to_persephone(
        company_director_data_dummy, stub_device_info
    )
    expected_result = {
        "unique_id": company_director_data_dummy.unique_id,
        "employ_status": company_director_data_dummy.employ_status,
        "employ_type": company_director_data_dummy.employ_type,
        "employ_position": company_director_data_dummy.employ_position,
        "employ_company_name": company_director_data_dummy.employ_company_name,
        "device_info": stub_device_info.device_info,
        "device_id": stub_device_info.device_id,
    }
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_employ_for_us(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    result = await EmployDataService.update_employ_for_us(
        company_director_request_dummy
    )
    expected_result = None

    assert result == expected_result
    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_employ_for_us_when_user_is_in_wrong_step(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock
):
    get_onboarding_step_mock.return_value = onboarding_step_incorrect_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    with pytest.raises(InvalidStepError):
        result = await EmployDataService.update_employ_for_us(
            company_director_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert not persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_employ_for_us_when_cant_send_to_persephone(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (False, 0)
    update_user_mock.return_value = True
    with pytest.raises(InternalServerError):
        result = await EmployDataService.update_employ_for_us(
            company_director_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepChecker, "get_onboarding_step")
async def test_update_employ_for_us_when_cant_update_user_register(
    get_onboarding_step_mock, persephone_client_mock, update_user_mock
):
    get_onboarding_step_mock.return_value = onboarding_step_correct_stub
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = False
    with pytest.raises(InternalServerError):
        result = await EmployDataService.update_employ_for_us(
            company_director_request_dummy
        )

    assert get_onboarding_step_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called
