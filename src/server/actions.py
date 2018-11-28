from enum import Enum

class Action(Enum):
	INIT = "init"
	NEXT_INGREDIENT = "next_ingredient"
	NEXT_ORDER = "next_order"
	NEW_ORDER = "new_order"
	CLEAR_QUEUE = "clear_queue"
	RESTART = "restart"
	BT_SETUP = "bt_setup"
	BT_READY = "bt_ready"
	REFRESH = "refresh"