import argparse
import re
from pathlib import Path

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--base-temp", type=float, default=318.5)
parser.add_argument("--transient", action="store_true")
parser.add_argument("--steady-state", action="store_true")
args = parser.parse_args()

model = args.model

main_py = Path("ARTSim.py")
global_vars = Path("src/globalVar.py")

text = main_py.read_text()

# Update model import
text = re.sub(
    r"from\s+models\.[a-zA-Z0-9_]+\s+import\s+model",
    f"from models.{model} import model",
    text
)

# Helper: enable or comment a function
def update_function(text, func_name, enable, log_name):
    pattern = re.compile(rf"(?:#\s*)?{func_name}\([^\)]*\)")
    if enable:
        replacement = f'{func_name}({log_name})' if func_name == 'runSteadyState' else f'{func_name}(stepDefinition, {log_name})'
        text = pattern.sub(replacement, text)
    else:
        # Ensure single comment, do not double-comment
        text = pattern.sub(lambda m: m.group(0) if m.group(0).startswith("#") else "# " + m.group(0), text)
    return text

# Update runTransient
text = update_function(
    text,
    "runTransient",
    args.transient,
    f'"logs/{model}_transientResult.log"'
)

# Update runSteadyState
text = update_function(
    text,
    "runSteadyState",
    args.steady_state,
    f'"logs/{model}_steadystate.log"'
)

# Write back
main_py.write_text(text)

# Update baseTemp
gv_text = global_vars.read_text()
gv_text = re.sub(
    r"^baseTemp\s*=.*$",
    f"baseTemp = {args.base_temp}",
    gv_text,
    flags=re.MULTILINE
)
global_vars.write_text(gv_text)
