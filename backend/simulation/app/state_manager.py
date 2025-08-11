import os  
import json  
import logging  
  
STATE_FILE = "simulation_state.json"  
logger = logging.getLogger(__name__)  
  
def get_state():  
    """Retrieve simulation state from state file."""  
    if not os.path.exists(STATE_FILE):  
        set_state("stopped")  # Default state is stopped  
    with open(STATE_FILE, "r") as f:  
        return json.load(f).get("state", "stopped")  
  
def set_state(state):  
    """Update simulation state in state file."""  
    with open(STATE_FILE, "w") as f:  
        json.dump({"state": state}, f)  
  
def is_running():  
    return get_state() == "running"  
  
def is_paused():  
    return get_state() == "paused"  
  
def is_stopped():  
    return get_state() == "stopped"  
