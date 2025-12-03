"""
Test suite for submit_fir isDrafted logic

Tests verify that:
1. isDrafted=True → Stage 0, Pending_At="Investigation Officer", no FIR_SUBMITTED event
2. isDrafted=False → Stage 1, Pending_At="Tribal Officer", FIR_SUBMITTED event created
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from app.routers.dbt import submit_fir_form
from app.schemas.dbt_schemas import AtrocityBase


class TestSubmitFirIsDrafted:
    """Test cases for isDrafted parameter behavior"""

    @pytest.fixture
    def mock_token_payload(self):
        """Mock JWT token payload for IO"""
        return {
            "sub": "io_officer_123",
            "role": "Investigation Officer",
            "state_ut": "Jharkhand",
            "district": "Ranchi",
            "vishesh_p_s_name": "Ranchi_PS"
        }

    @pytest.fixture
    def mock_uploaded_file(self):
        """Mock uploaded file"""
        file = Mock()
        file.filename = "test_file.pdf"
        file.file = b"test content"
        return file

    @pytest.fixture
    def mock_fir_data(self):
        """Mock FIR data from government database"""
        data = Mock()
        data.incident_summary = "Atrocity case involving SC/ST community"
        data.victim_name = "Ram Kumar"
        data.complainant_name = "Ram Kumar"
        data.complainant_relation = "Self"
        data.complainant_contact = "9876543210"
        data.sections_invoked = "SC/ST Act 1989"
        data.incident_location = "Ranchi, Jharkhand"
        data.incident_date = "2025-01-10"
        return data

    @pytest.fixture
    def mock_aadhaar_data(self):
        """Mock Aadhaar data from government database"""
        data = Mock()
        data.father_name = "Mohan Kumar"
        data.dob = "1990-05-15"
        data.gender = "M"
        data.mobile = "9876543210"
        return data

    @patch('app.routers.dbt.get_fir_by_number')
    @patch('app.routers.dbt.get_aadhaar_by_number')
    @patch('app.routers.dbt.save_uploaded_file')
    @patch('app.routers.dbt.insert_case_event')
    @patch('app.routers.dbt.insert_atrocity_case')
    async def test_submit_fir_draft_true(
        self,
        mock_insert_case,
        mock_insert_event,
        mock_save_file,
        mock_aadhaar,
        mock_fir,
        mock_token_payload,
        mock_uploaded_file,
        mock_fir_data,
        mock_aadhaar_data
    ):
        """
        Test: isDrafted=True
        Expected: Stage=0, Pending_At="Investigation Officer", NO event inserted
        """
        # Setup mocks
        mock_fir.return_value = mock_fir_data
        mock_aadhaar.return_value = mock_aadhaar_data
        mock_save_file.return_value = "saved_file_path.pdf"
        mock_insert_case.return_value = {"Case_No": 1001, "message": "Success"}
        mock_insert_event.return_value = None

        # Call endpoint with isDrafted=True
        response = await submit_fir_form(
            isDrafted=True,
            firNumber="FIR-2025-001",
            caste="SC",
            aadhaar="123456789012",
            email="victim@email.com",
            photo=mock_uploaded_file,
            firDocument=mock_uploaded_file,
            casteCertificate=mock_uploaded_file,
            medicalCertificate=None,
            postmortem=None,
            accountNumber="1234567890",
            ifscCode="BANK0001",
            holderName="Victim Name",
            bankName="SBI",
            token_payload=mock_token_payload
        )

        # Assertions for draft case
        assert response["case_no"] == 1001
        assert response["fir_no"] == "FIR-2025-001"
        assert response["stage"] == 0, "Stage should be 0 for draft"
        assert response["pending_at"] == "Investigation Officer", "Pending_At should be IO for draft"
        assert response["is_drafted"] == True, "is_drafted flag should be True"
        assert "draft" in response["message"].lower(), "Message should indicate draft"

        # Verify that insert_atrocity_case was called with Stage=0
        call_args = mock_insert_case.call_args[0][0]  # Get the data dict argument
        assert call_args["Stage"] == 0, "ATROCITY table should have Stage=0"
        assert call_args["Pending_At"] == "Investigation Officer", "ATROCITY table should have Pending_At=IO"

        # Verify that NO event was inserted for draft
        mock_insert_event.assert_not_called(), "FIR_SUBMITTED event should NOT be inserted for draft"
        print("✓ Test passed: isDrafted=True → Stage 0, no event")

    @patch('app.routers.dbt.get_fir_by_number')
    @patch('app.routers.dbt.get_aadhaar_by_number')
    @patch('app.routers.dbt.save_uploaded_file')
    @patch('app.routers.dbt.insert_case_event')
    @patch('app.routers.dbt.insert_atrocity_case')
    async def test_submit_fir_draft_false(
        self,
        mock_insert_case,
        mock_insert_event,
        mock_save_file,
        mock_aadhaar,
        mock_fir,
        mock_token_payload,
        mock_uploaded_file,
        mock_fir_data,
        mock_aadhaar_data
    ):
        """
        Test: isDrafted=False (default)
        Expected: Stage=1, Pending_At="Tribal Officer", FIR_SUBMITTED event inserted
        """
        # Setup mocks
        mock_fir.return_value = mock_fir_data
        mock_aadhaar.return_value = mock_aadhaar_data
        mock_save_file.return_value = "saved_file_path.pdf"
        mock_insert_case.return_value = {"Case_No": 1002, "message": "Success"}
        mock_insert_event.return_value = None

        # Call endpoint with isDrafted=False (default)
        response = await submit_fir_form(
            isDrafted=False,  # Submit, not draft
            firNumber="FIR-2025-002",
            caste="ST",
            aadhaar="123456789013",
            email="victim2@email.com",
            photo=mock_uploaded_file,
            firDocument=mock_uploaded_file,
            casteCertificate=mock_uploaded_file,
            medicalCertificate=None,
            postmortem=None,
            accountNumber="1234567891",
            ifscCode="BANK0002",
            holderName="Victim 2 Name",
            bankName="ICICI",
            token_payload=mock_token_payload
        )

        # Assertions for submitted case
        assert response["case_no"] == 1002
        assert response["fir_no"] == "FIR-2025-002"
        assert response["stage"] == 1, "Stage should be 1 for final submit"
        assert response["pending_at"] == "Tribal Officer", "Pending_At should be TO for final submit"
        assert response["is_drafted"] == False, "is_drafted flag should be False"
        assert "submitted" in response["message"].lower(), "Message should indicate submission"

        # Verify that insert_atrocity_case was called with Stage=1
        call_args = mock_insert_case.call_args[0][0]  # Get the data dict argument
        assert call_args["Stage"] == 1, "ATROCITY table should have Stage=1"
        assert call_args["Pending_At"] == "Tribal Officer", "ATROCITY table should have Pending_At=TO"

        # Verify that FIR_SUBMITTED event WAS inserted for final submit
        mock_insert_event.assert_called_once()
        event_call = mock_insert_event.call_args[1]  # Get kwargs
        assert event_call["event_type"] == "FIR_SUBMITTED", "Event type should be FIR_SUBMITTED"
        assert event_call["performed_by"] == "io_officer_123", "Event should be by IO"
        assert event_call["performed_by_role"] == "Investigation Officer", "Event role should be IO"
        assert event_call["case_no"] == 1002, "Event should be for case 1002"
        print("✓ Test passed: isDrafted=False → Stage 1, FIR_SUBMITTED event inserted")

    @patch('app.routers.dbt.get_fir_by_number')
    @patch('app.routers.dbt.get_aadhaar_by_number')
    @patch('app.routers.dbt.save_uploaded_file')
    @patch('app.routers.dbt.insert_case_event')
    @patch('app.routers.dbt.insert_atrocity_case')
    async def test_submit_fir_jurisdiction_captured(
        self,
        mock_insert_case,
        mock_insert_event,
        mock_save_file,
        mock_aadhaar,
        mock_fir,
        mock_token_payload,
        mock_uploaded_file,
        mock_fir_data,
        mock_aadhaar_data
    ):
        """
        Test: Jurisdiction fields from JWT token are properly captured
        Expected: State_UT, District, Vishesh_P_S_Name from JWT are in ATROCITY record
        """
        # Setup mocks
        mock_fir.return_value = mock_fir_data
        mock_aadhaar.return_value = mock_aadhaar_data
        mock_save_file.return_value = "saved_file_path.pdf"
        mock_insert_case.return_value = {"Case_No": 1003, "message": "Success"}

        # Call endpoint
        await submit_fir_form(
            isDrafted=False,
            firNumber="FIR-2025-003",
            caste="SC",
            aadhaar="123456789014",
            email="victim3@email.com",
            photo=mock_uploaded_file,
            firDocument=mock_uploaded_file,
            casteCertificate=mock_uploaded_file,
            medicalCertificate=None,
            postmortem=None,
            accountNumber="1234567892",
            ifscCode="BANK0003",
            holderName="Victim 3 Name",
            bankName="PNB",
            token_payload=mock_token_payload
        )

        # Verify jurisdiction fields from JWT token are captured
        call_args = mock_insert_case.call_args[0][0]  # Get the data dict argument
        assert call_args["State_UT"] == "Jharkhand", "State_UT should be from JWT"
        assert call_args["District"] == "Ranchi", "District should be from JWT"
        assert call_args["Vishesh_P_S_Name"] == "Ranchi_PS", "Vishesh_P_S_Name should be from JWT"
        print("✓ Test passed: Jurisdiction fields properly captured from JWT")


# Standalone test runner (can be run with: python test_submit_fir_isdrafted.py)
if __name__ == "__main__":
    print("Run with: pytest tests/test_submit_fir_isdrafted.py -v")
    print("Or: pytest tests/test_submit_fir_isdrafted.py -s (for print statements)")
