import yaml
import importlib
from pathlib import Path
from openagentcli.ui import Colors

def load_config() -> dict:
    config_path = Path(__file__).parent.parent / 'config.yaml'
    if not config_path.exists():
        print(f"\n{Colors.ERROR}config.yaml not found{Colors.RESET}")
        print(f"{Colors.DIM}Create config.yaml in the project root with:{Colors.RESET}")
        print(f"{Colors.DIM}model_config:{Colors.RESET}")
        print(f"{Colors.DIM}  file_name: cohere_model{Colors.RESET}")
        print(f"{Colors.DIM}  class_name: CohereModel{Colors.RESET}\n")
        exit(1)
    
    try:
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"\n{Colors.ERROR}Invalid YAML in config.yaml{Colors.RESET}")
        print(f"{Colors.DIM}{str(e)}{Colors.RESET}\n")
        exit(1)

def load_model(config: dict):
    model_config = config.get('model_config')
    
    if model_config is None:
        print(f"\n{Colors.ERROR}Missing 'model_config' in config.yaml{Colors.RESET}")
        print(f"{Colors.DIM}Expected structure:{Colors.RESET}")
        print(f"{Colors.DIM}model_config:{Colors.RESET}")
        print(f"{Colors.DIM}  file_name: cohere_model{Colors.RESET}")
        print(f"{Colors.DIM}  class_name: CohereModel{Colors.RESET}\n")
        exit(1)
    
    if not isinstance(model_config, dict):
        print(f"\n{Colors.ERROR}'model_config' must be a dictionary{Colors.RESET}")
        print(f"{Colors.DIM}Check your config.yaml indentation.{Colors.RESET}\n")
        exit(1)
    
    model_file = model_config.get('file_name')
    model_class = model_config.get('class_name')
    
    if not model_file:
        print(f"\n{Colors.ERROR}Missing 'file_name' in model_config{Colors.RESET}")
        print(f"{Colors.DIM}Add: file_name: your_model_file{Colors.RESET}\n")
        exit(1)
    
    if not model_class:
        print(f"\n{Colors.ERROR}Missing 'class_name' in model_config{Colors.RESET}")
        print(f"{Colors.DIM}Add: class_name: YourModelClass{Colors.RESET}\n")
        exit(1)
    
    custom_instructions = config.get('custom_instructions')
    
    try:
        module = importlib.import_module(f'openagentcli.models.{model_file}')
    except ModuleNotFoundError:
        print(f"\n{Colors.ERROR}Model file '{model_file}' not found in openagentcli/models/{Colors.RESET}")
        print(f"{Colors.DIM}Check your config.yaml and ensure the file exists.{Colors.RESET}\n")
        exit(1)
    
    try:
        model_cls = getattr(module, model_class)
    except AttributeError:
        print(f"\n{Colors.ERROR}Class '{model_class}' not found in {model_file}.py{Colors.RESET}")
        print(f"{Colors.DIM}Check your config.yaml and ensure the class name is correct.{Colors.RESET}\n")
        exit(1)
    
    return model_cls(custom_instructions=custom_instructions)
