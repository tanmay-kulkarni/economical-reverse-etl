import json
from aws_cdk import App
from stacks.etl_stack import EtlStack

app = App()

# Load configs for each environment
def load_config(env_name: str) -> dict:
    config_path = f"../deploy/config/{env_name}.json"
    with open(config_path, 'r') as f:
        return json.load(f)

# Create stacks with their respective configs
EtlStack(app, "EtlStackDev", 
         env_name="dev", 
         config=load_config("dev"))

EtlStack(app, "EtlStackStaging", 
         env_name="staging", 
         config=load_config("staging"))

EtlStack(app, "EtlStackProd", 
         env_name="prod", 
         config=load_config("prod"))

app.synth()