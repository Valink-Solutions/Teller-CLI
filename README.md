# Teller-CLI for ChunkVault-Lite

Teller-CLI is an open source Python/Typer-based CLI tool for uploading Minecraft world backups to ChunkVault-Lite, an open source backup solution provided by Valink Solutions.

Checkout the [Technical Write-Up](https://dev.to/valink/crafting-robust-minecraft-backup-tools-a-deep-dive-into-chunkvault-lite-and-teller-cli-16d1) which explains how Teller-CLI works and how to install it.

## Testing

Limited testing was done on MacOS 13 and Windows 10

## Usage

To use Teller-CLI, first install the tool:

```bash
    pip install teller-cli
```

Then, run the following command to create a snapshot:

```bash
    teller-cli upload "/path/to/world"
```

This will upload the specified backup to ChunkVault-Lite.

### First Launch

On first launch, Teller-CLI will prompt you to enter the API URL for your ChunkVault-Lite instance. The trailing slash is not necessary, so you can enter the URL without it.

After entering the API URL, Teller-CLI will prompt you to enter your API token. You can obtain this token from your ChunkVault-Lite instance. This token is required for authentication purposes and allows Teller-CLI to access your backups.

Once you have entered the API URL and token, Teller-CLI will store this information locally for future use. You can update this information at any time by running the `teller-cli config` command.

---

## Additional Information

ChunkVault-Lite is hosted in a separatly. For more information on ChunkVault-Lite visit the [Repository](https://github.com/Valink-Solutions/ChunkVault-Lite)
