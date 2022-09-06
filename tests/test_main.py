from unittest.mock import patch

import decouple
from etria_logger import Gladsheim
from flask import Flask
from heimdall_client.bifrost import Heimdall, HeimdallStatusResponses
from pytest import mark
from werkzeug.test import Headers

with patch.object(decouple, "config", return_value=""):
    from main import update_employ_for_us
    from src.domain.exceptions.model import (
        InvalidStepError,
        InternalServerError,
    )
    from src.services.employ_data.service import EmployDataService

request_ok = {
    "user_employ_status": "EMPLOYED",
    "user_employ_type": "UTILITIES",
    "user_employ_position": "ADMINISTRATOR",
    "user_employ_company_name": "CAESAR Inc.",
}
requests_invalid = [
    {
        "user_employ_statu": "EMPLOYED",
        "user_employ_typ": "UTILITIES",
        "user_employ_poition": "ADMINISTRATOR",
        "user_employ_cmpany_name": "CAESAR Inc.",
    },
    {
        "user_employ_status": "EMPLOYE",
        "user_employ_type": "UTILITIES",
        "user_employ_position": "ADMINISTRATOR",
        "user_employ_company_name": "CAESAR Inc.",
    },
    {
        "user_employ_status": "EMPLOYED",
        "user_employ_type": "UTILITIE",
        "user_employ_position": "ADMINISTRATOR",
        "user_employ_company_name": "CAESAR Inc.",
    },
    {
        "user_employ_status": "EMPLOYED",
        "user_employ_type": "UTILITIES",
        "user_employ_position": "ADMINISTRATO",
        "user_employ_company_name": "CAESAR Inc.",
    },
    {
        "user_employ_status": "EMPLOYED",
        "user_employ_type": "UTILITIES",
        "user_employ_position": "ADMINISTRATOR",
        "user_employ_company_name": "",
    },
]

decoded_jwt_ok = {
    "is_payload_decoded": True,
    "decoded_jwt": {"user": {"unique_id": "test"}},
    "message": "Jwt decoded",
}
decoded_jwt_invalid = {
    "is_payload_decoded": False,
    "decoded_jwt": {"user": {"unique_id": "test_error"}},
    "message": "Jwt decoded",
}


@mark.asyncio
@patch.object(Heimdall, "decode_payload")
@patch.object(EmployDataService, "update_employ_for_us")
async def test_update_employ_for_us_when_request_is_ok(
    update_employ_for_us_residence_mock,
    decode_payload_mock,
):
    update_employ_for_us_residence_mock.return_value = None
    decode_payload_mock.return_value = (decoded_jwt_ok, HeimdallStatusResponses.SUCCESS)

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_employ_for_us(request)

        assert (
            result.data
            == b'{"result": null, "message": "Register Updated.", "success": true, "code": 0}'
        )
        assert update_employ_for_us_residence_mock.called


@mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(Heimdall, "decode_payload")
@patch.object(EmployDataService, "update_employ_for_us")
async def test_update_employ_for_us_when_jwt_is_invalid(
    update_employ_for_us_residence_mock,
    decode_payload_mock,
    etria_mock,
):
    update_employ_for_us_residence_mock.return_value = None
    decode_payload_mock.return_value = (
        decoded_jwt_invalid,
        HeimdallStatusResponses.INVALID_TOKEN,
    )

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_employ_for_us(request)

        assert (
            result.data
            == b'{"result": null, "message": "JWT invalid or not supplied", "success": false, "code": 30}'
        )
        assert not update_employ_for_us_residence_mock.called
        assert etria_mock.called


@mark.asyncio
@mark.parametrize("requests", requests_invalid)
@patch.object(Heimdall, "decode_payload")
@patch.object(Gladsheim, "error")
@patch.object(EmployDataService, "update_employ_for_us")
async def test_update_employ_for_us_when_request_is_invalid(
    update_employ_for_us_residence_mock,
    etria_mock,
    decode_payload_mock,
    requests,
):
    update_employ_for_us_residence_mock.return_value = None
    decode_payload_mock.return_value = (decoded_jwt_ok, HeimdallStatusResponses.SUCCESS)

    app = Flask(__name__)
    with app.test_request_context(
        json=requests,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_employ_for_us(request)

        assert (
            result.data
            == b'{"result": null, "message": "Invalid parameters", "success": false, "code": 10}'
        )
        assert not update_employ_for_us_residence_mock.called
        etria_mock.assert_called()


@mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(Heimdall, "decode_payload")
@patch.object(EmployDataService, "update_employ_for_us")
async def test_update_employ_for_us_when_user_is_in_invalid_oboarding_step(
    update_employ_for_us_residence_mock,
    decode_payload_mock,
    etria_mock,
):
    update_employ_for_us_residence_mock.side_effect = InvalidStepError("errooou")
    decode_payload_mock.return_value = (
        decoded_jwt_ok,
        HeimdallStatusResponses.SUCCESS,
    )

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_employ_for_us(request)

        assert (
            result.data
            == b'{"result": null, "message": "User in invalid onboarding step", "success": false, "code": 10}'
        )
        assert update_employ_for_us_residence_mock.called
        assert etria_mock.called


@mark.asyncio
@patch.object(Gladsheim, "error")
@patch.object(Heimdall, "decode_payload")
@patch.object(EmployDataService, "update_employ_for_us")
async def test_update_employ_for_us_when_internal_server_error_occurs(
    update_employ_for_us_residence_mock,
    decode_payload_mock,
    etria_mock,
):
    update_employ_for_us_residence_mock.side_effect = InternalServerError("errooou")
    decode_payload_mock.return_value = (
        decoded_jwt_ok,
        HeimdallStatusResponses.SUCCESS,
    )

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_employ_for_us(request)

        assert (
            result.data
            == b'{"result": null, "message": "Failed to update register", "success": false, "code": 100}'
        )
        assert update_employ_for_us_residence_mock.called
        assert etria_mock.called


@mark.asyncio
@patch.object(Heimdall, "decode_payload")
@patch.object(Gladsheim, "error")
@patch.object(EmployDataService, "update_employ_for_us")
async def test_update_employ_for_us_when_generic_exception_happens(
    update_employ_for_us_residence_mock,
    etria_mock,
    decode_payload_mock,
):
    update_employ_for_us_residence_mock.side_effect = Exception("erro")
    decode_payload_mock.return_value = (decoded_jwt_ok, HeimdallStatusResponses.SUCCESS)

    app = Flask(__name__)
    with app.test_request_context(
        json=request_ok,
        headers=Headers({"x-thebes-answer": "test"}),
    ).request as request:

        result = await update_employ_for_us(request)

        assert (
            result.data
            == b'{"result": null, "message": "Unexpected error occurred", "success": false, "code": 100}'
        )
        assert update_employ_for_us_residence_mock.called
        etria_mock.assert_called()
