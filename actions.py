from enum import Enum

class Action(Enum):
	USE_INGREDIENT = "use_ingredient"
	NEXT_ORDER = "next_order"
	NEW_ORDER = "new_order"
	CLEAR_QUEUE = "clear_queue"
