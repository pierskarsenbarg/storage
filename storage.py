import pulumi
from pulumi_azure_native import storage
from typing import Optional, TypedDict

class StorageArgs(TypedDict):
    """
    TypedDict for storage resource arguments.

    Attributes:
        resource_group_name (pulumi.Output[str]): The name of the resource group in which to create the storage resources.
    """
    resource_group_name: pulumi.Output[str]

class Storage(pulumi.ComponentResource):
    """
    Storage is a Pulumi ComponentResource that provisions an Azure Storage Account and a Blob Container within it.

    Attributes:
        blob_container_name (pulumi.Output[str]): The name of the created blob container.
        storage_account_name (pulumi.Output[str]): The name of the created storage account.
        storage_account_primary_key (pulumi.Output[str]): The primary key of the created storage account.

    Example:

    ```python
        storage = Storage(
            "my-storage",
            StorageArgs(resource_group_name="my-resource-group")
        )
    ```

    ```typescript
        const storage = new Storage("my-storage", {
            resourceGroupName: "my-resource-group",
        });
    ```    
    This component creates an Azure Storage Account and a Blob Container, and exports the primary key for the storage account.
    """
    blob_container_name: pulumi.Output[str]
    storage_account_name: pulumi.Output[str]
    storage_account_primary_key: pulumi.Output[str]
    
    def __init__(self, name: str, args: StorageArgs, opts: Optional[pulumi.ResourceOptions] = None): 
        """
        Creates a new Storage resource.

        Arguments:
            name (str): The unique name of the storage resource.
            args (StorageArgs): Arguments required to configure the storage resource, such as resource group name.
            opts (Optional[pulumi.ResourceOptions], optional): Resource options for the Pulumi resource. Defaults to None.

        Outputs:
            blob_container_name (pulumi.Output): The name of the created blob container.
            storage_account_name (pulumi.Output): The name of the created storage account.
            storage_account_primary_key (pulumi.Output): The primary key of the created storage account.

        :param pulumi.Input[str] resource_group_name: Name of resource group that the resources are part of
        """
        super().__init__("x:index:Storage", name, {}, opts)

        if (opts == None):
            opts = pulumi.ResourceOptions()

        opts.parent = self

        resource_group_name = args.get("resource_group_name")

        account = storage.StorageAccount(
            "sa",
            resource_group_name=resource_group_name,
            sku={
                "name": storage.SkuName.STANDARD_LRS,
            },
            kind=storage.Kind.STORAGE_V2,
            opts=opts
        )

        blob_container = storage.BlobContainer(
            f"{name}-blobcontainer",
            account_name=account.name,
            resource_group_name=resource_group_name,
            opts=opts
        )

        # Export the primary key of the Storage Account
        primary_key = (
            pulumi.Output.all(resource_group_name, account.name)
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
