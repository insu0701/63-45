OAUTH_TOKEN_PATH = "/oauth2/token"

# Account-domain resource path.
# Official docs explicitly show ka00001 (계좌번호조회) on /api/dostk/acnt.
# Keep all account TRs centralized here so you can change one line if Kiwoom's docs
# for your environment/version differ.
ACCOUNT_RESOURCE_PATH = "/api/dostk/acnt"

API_ID_ACCOUNT_NUMBERS = "ka00001"
API_ID_CASH = "kt00001"
API_ID_DAILY_STATUS = "kt00017"
API_ID_HOLDINGS = "kt00018"

DEFAULT_TIMEOUT_SECONDS = 15