"""Shared pytest fixtures."""

import pytest

from crs.english import EnglishService
from crs.french import FrenchService
from crs.service import CRSService
from crs.transferability import TransferabilityService
from eligibility.service import EligibilityService


@pytest.fixture
def english_service():
    """Create a fresh english service instance before each test"""
    return EnglishService()


@pytest.fixture
def french_service():
    """Create a fresh french service instance before each test"""
    return FrenchService()


@pytest.fixture
def transferability_service(english_service, french_service):
    """Real TransferabilityService, it's pure, no need to mock its deps"""
    return TransferabilityService(
        english_service=english_service, french_service=french_service
    )


@pytest.fixture
def crs_service(english_service, french_service, transferability_service):
    """Real CRSService, it's pure, no need to mock its deps"""
    return CRSService(
        english_service=english_service,
        french_service=french_service,
        transferability_service=transferability_service,
    )


@pytest.fixture
def eligibility_service():
    """Create a fresh eligibility service instance before each test"""
    return EligibilityService()
