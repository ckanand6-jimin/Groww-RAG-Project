from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GROWW_HDFC_FUNDS = {
    "hdfc_mid_cap_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "hdfc_large_cap_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "hdfc_small_cap_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "hdfc_equity_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "hdfc_elss_tax_saver_fund_direct_plan_growth": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "hdfc_balanced_advantage_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth",
    "hdfc_nifty_50_index_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth",
    "hdfc_defence_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "hdfc_gold_etf_fund_of_fund_direct_plan_growth": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "hdfc_liquid_fund_direct_growth": "https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth",
}

HDFC_OFFICIAL_SOURCES = {
    "kim": "https://www.hdfcfund.com/investor-services/fund-documents/kim",
    "sid": "https://www.hdfcfund.com/investor-services/fund-documents/sid",
    "online_services": "https://www.hdfcfund.com/information/online-services-investors",
    "consolidated_account_statement": "https://www.hdfcfund.com/services/consolidated-account-statement",
}

AMFI_SEBI_RESOURCES = {
    "amfi_investor": "https://www.amfiindia.com/investor",
    "sebi_understanding_mf": "https://investor.sebi.gov.in/understanding_mf.html",
}

SCHEME_METADATA = {
    "hdfc_mid_cap_fund_direct_growth": {
        "scheme_name": "HDFC Mid Cap Fund",
        "scheme_type": "Equity",
        "category": "Equity > Mid Cap",
    },
    "hdfc_large_cap_fund_direct_growth": {
        "scheme_name": "HDFC Large Cap Fund",
        "scheme_type": "Equity",
        "category": "Equity > Large Cap",
    },
    "hdfc_small_cap_fund_direct_growth": {
        "scheme_name": "HDFC Small Cap Fund",
        "scheme_type": "Equity",
        "category": "Equity > Small Cap",
    },
    "hdfc_equity_fund_direct_growth": {
        "scheme_name": "HDFC Equity Fund",
        "scheme_type": "Equity",
        "category": "Equity > Diversified",
    },
    "hdfc_elss_tax_saver_fund_direct_plan_growth": {
        "scheme_name": "HDFC ELSS Tax Saver Fund",
        "scheme_type": "ELSS",
        "category": "Equity > ELSS",
    },
    "hdfc_balanced_advantage_fund_direct_growth": {
        "scheme_name": "HDFC Balanced Advantage Fund",
        "scheme_type": "Hybrid",
        "category": "Hybrid > Dynamic Asset Allocation",
    },
    "hdfc_nifty_50_index_fund_direct_growth": {
        "scheme_name": "HDFC Nifty 50 Index Fund",
        "scheme_type": "Index",
        "category": "Equity > Index",
    },
    "hdfc_defence_fund_direct_growth": {
        "scheme_name": "HDFC Defence Fund",
        "scheme_type": "Equity",
        "category": "Equity > Sectoral",
    },
    "hdfc_gold_etf_fund_of_fund_direct_plan_growth": {
        "scheme_name": "HDFC Gold ETF Fund of Fund",
        "scheme_type": "Commodity",
        "category": "ETFs > Gold",
    },
    "hdfc_liquid_fund_direct_growth": {
        "scheme_name": "HDFC Liquid Fund",
        "scheme_type": "Debt",
        "category": "Debt > Liquid",
    },
}

ALL_SOURCE_URLS = list(GROWW_HDFC_FUNDS.values()) + list(HDFC_OFFICIAL_SOURCES.values()) + list(AMFI_SEBI_RESOURCES.values())
