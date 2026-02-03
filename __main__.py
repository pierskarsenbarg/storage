from pulumi.provider.experimental import component_provider_host
from storage import Storage

if __name__ == "__main__":
    component_provider_host(name="storage", components=[Storage])