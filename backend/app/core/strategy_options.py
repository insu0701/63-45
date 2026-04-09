STRATEGY_STATE_OPTIONS = [
    "STATE_0",
    "STATE_1",
    "STATE_2",
    "STATE_3",
]

TARGET_STATE_OPTIONS = [
    "STATE_0",
    "STATE_1",
    "STATE_2",
    "STATE_3",
]

ELIGIBILITY_STATUS_OPTIONS = [
    "unknown",
    "eligible",
    "ineligible",
    "blocked",
]

BUY_LIST_STATUS_OPTIONS = [
    "unknown",
    "in_buy_list",
    "out_of_buy_list",
    "held_not_buyable",
]

REASON_CODE_OPTIONS = [
    {
        "code": "MANUAL_PLACEHOLDER",
        "label": "Manual Placeholder",
        "description": "Placeholder row with no real review yet.",
    },
    {
        "code": "MANUAL_HOLD",
        "label": "Manual Hold",
        "description": "Keep the current position unchanged after review.",
    },
    {
        "code": "MANUAL_ACCUMULATE",
        "label": "Manual Accumulate",
        "description": "Increase desired exposure or keep a constructive bias.",
    },
    {
        "code": "MANUAL_TRIM",
        "label": "Manual Trim",
        "description": "Reduce desired exposure without a full exit.",
    },
    {
        "code": "MANUAL_EXIT",
        "label": "Manual Exit",
        "description": "Move the name toward a full exit state.",
    },
    {
        "code": "MANUAL_WAIT_SIGNAL",
        "label": "Manual Wait",
        "description": "Wait for clearer confirmation before changing exposure.",
    },
    {
        "code": "MANUAL_BLOCK_RISK",
        "label": "Risk Block",
        "description": "Do not add because of concentration, liquidity, or another risk concern.",
    },
    {
        "code": "MANUAL_BLOCK_UNIVERSE",
        "label": "Universe Block",
        "description": "Do not add because the name is not buy-eligible.",
    },
    {
        "code": "MANUAL_TARGET_SET",
        "label": "Target Set",
        "description": "A manual target state or target size was set explicitly.",
    },
    {
        "code": "MANUAL_REVIEW_REQUIRED",
        "label": "Review Required",
        "description": "Name requires further review before the next action.",
    },
]

ALLOWED_REASON_CODES = {item["code"] for item in REASON_CODE_OPTIONS}
ALLOWED_STRATEGY_STATES = set(STRATEGY_STATE_OPTIONS)
ALLOWED_TARGET_STATES = set(TARGET_STATE_OPTIONS)
ALLOWED_ELIGIBILITY_STATUSES = set(ELIGIBILITY_STATUS_OPTIONS)
ALLOWED_BUY_LIST_STATUSES = set(BUY_LIST_STATUS_OPTIONS)