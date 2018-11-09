from enum import Enum


class DialogActionType(Enum):
    ELICIT_SLOT = "ElicitSlot"
    ELICIT_INTENT = "ElicitIntent"
    CONFIRM_INTENT = "ConfirmIntent"
    DELEGATE = "Delegate"
    CLOSE = "Close"
