import pulumi
from pulumi_azure_native import storage
from typing import Optional, TypedDict

class StorageArgs(TypedDict):
    resource_group_name: pulumi.Output[str]

class Storage(pulumi.ComponentResource):
    storage_account_primary_key: pulumi.Output[str]
    blob_container_name: pulumi.Output[str]
    storage_account_name: pulumi.Output[str]
    def __init__(self, name: str, args: StorageArgs, opts: Optional[pulumi.ResourceOptions] = None): 
        super().__init__("x:index:Storage", name, {}, opts)

        if (opts == None):
            opts = pulumi.ResourceOptions()

        opts.parent = self

        account = storage.StorageAccount(
            "sa",
            resource_group_name=args.get("resource_group_name"),
            sku={
                "name": storage.SkuName.STANDARD_LRS,
            },
            kind=storage.Kind.STORAGE_V2,
            opts=opts
        )

        blob_container = storage.BlobContainer(
            f"{name}-blobcontainer",
            account_name=account.name,
            resource_group_name=args.get("resource_group_name"),
            opts=opts
        )

        # Export the primary key of the Storage Account
        primary_key = (
            pulumi.Output.all(args.get("resource_group_name"), account.name)
            .apply(
                lambda args: storage.list_storage_account_keys(
                    resource_group_name=args[0], account_name=args[1]
                )
            )
            .apply(lambda accountKeys: accountKeys.keys[0].value)
        )

        self.blob_container_name = blob_container.name
        self.storage_account_name = account.name
        self.storage_account_primary_key = primary_key

        self.register_outputs({
            "blob_container_name": self.blob_container_name,
            "storage_account_name": self.storage_account_name,
            "storage_account_primary_key": self.storage_account_primary_key
        })
