from unittest.mock import patch

import pytest
from persephone_client import Persephone

from src.domain.exceptions.model import InternalServerError
from src.domain.models.request.model import EmployForUs
from src.repositories.step_validator.repository import StepValidator
from src.repositories.user.repository import UserRepository
from src.services.employ_data.service import EmployDataService

tax_residence_model_dummy = EmployForUs(
    **{
        "user_employ_status": "EMPLOYED",
        "user_employ_type": "UTILITIES",
        "user_employ_position": "ADMINISTRATOR",
        "user_employ_company_name": "CAESAR Inc.",
    }
)

payload_dummy = {
    "x_thebes_answer": "x_thebes_answer",
    "data": {"user": {"unique_id": "unique_id"}},
}


def test___model_employ_data_to_persephone():
    employ_status = "string"
    employ_type = "string"
    employ_position = "string"
    employ_company_name = "string"
    unique_id = "string"
    result = EmployDataService._EmployDataService__model_employ_data_to_persephone(
        employ_status,
        employ_type,
        employ_position,
        employ_company_name,
        unique_id,
    )
    expected_result = {
        "unique_id": unique_id,
        "employ_status": employ_status,
        "employ_type": employ_type,
        "employ_position": employ_position,
        "employ_company_name": employ_company_name,
    }
    assert result == expected_result


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_employ_for_us(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = True
    result = await EmployDataService.update_employ_for_us(
        tax_residence_model_dummy, payload_dummy
    )
    expected_result = None

    assert result == expected_result
    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_employ_for_us_when_cant_send_to_persephone(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (False, 0)
    update_user_mock.return_value = True
    with pytest.raises(InternalServerError):
        result = await EmployDataService.update_employ_for_us(
            tax_residence_model_dummy, payload_dummy
        )

    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert not update_user_mock.called


@pytest.mark.asyncio
@patch.object(UserRepository, "update_user")
@patch.object(Persephone, "send_to_persephone")
@patch.object(StepValidator, "validate_onboarding_step")
async def test_update_employ_for_us_when_cant_update_user_register(
    step_validator_mock, persephone_client_mock, update_user_mock
):
    persephone_client_mock.return_value = (True, 0)
    update_user_mock.return_value = False
    with pytest.raises(InternalServerError):
        result = await EmployDataService.update_employ_for_us(
            tax_residence_model_dummy, payload_dummy
        )

    assert step_validator_mock.called
    assert persephone_client_mock.called
    assert update_user_mock.called
