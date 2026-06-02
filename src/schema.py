from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any


class DocumentLinks(BaseModel):
    kim_link: Optional[HttpUrl]
    sid_link: Optional[HttpUrl]
    factsheet_link: Optional[HttpUrl]
    prospectus_link: Optional[HttpUrl]


class AccountServices(BaseModel):
    statement_download_link: Optional[HttpUrl]
    statement_frequency: Optional[str]
    capital_gains_cert_availability: Optional[bool]
    account_statement_process: Optional[str]
    online_services_link: Optional[HttpUrl]


class SourceInfo(BaseModel):
    groww_url: Optional[HttpUrl]
    hdfc_official_url: Optional[HttpUrl]
    last_updated: Optional[str]
    data_version: Optional[int]


class FundScheme(BaseModel):
    scheme_id: str
    scheme_name: str
    scheme_type: Optional[str]
    category: Optional[str]
    expense_ratio: Optional[str]
    minimum_investment_lump_sum: Optional[str]
    minimum_investment_sip: Optional[str]
    exit_load: Optional[str]
    exit_load_applicability: Optional[str]
    lock_in_period: Optional[str]
    riskometer_class: Optional[str]
    benchmark_index: Optional[str]
    fund_manager_name: Optional[str]
    fund_manager_experience_years: Optional[int]
    current_aum: Optional[str]
    inception_date: Optional[str]
    scheme_text: Optional[str]
    sections: Optional[Dict[str, Any]]
    structured_fields: Optional[Dict[str, Any]]
    documents: Optional[DocumentLinks]
    account_services: Optional[AccountServices]
    sources: Optional[SourceInfo]
