# Teller-CLI for ChunkVault-Lite

Teller-CLI is an open source Python/Typer-based CLI tool for uploading Minecraft world backups to ChunkVault-Lite, an open source backup solution provided by Valink Solutions.

## Testing

Not tested on anything other than MacOS 13.2.1.

## Usage

To use Teller-CLI, first install the tool:

```bash
    poetry install
```

Then, run the following command to upload a backup:

```bash
    teller-cli upload "/path/to/world/backup.zip"
```

This will upload the specified backup to ChunkVault-Lite.

### First Launch

On first launch, Teller-CLI will prompt you to enter the API URL for your ChunkVault-Lite instance. The trailing slash is not necessary, so you can enter the URL without it.

After entering the API URL, Teller-CLI will prompt you to enter your API token. You can obtain this token from your ChunkVault-Lite instance. This token is required for authentication purposes and allows Teller-CLI to access your backups.

<!-- Once you have entered the API URL and token, Teller-CLI will store this information locally for future use. You can update this information at any time by running the `teller-cli config` command. -->

---

## Additional Information

ChunkVault-Lite is hosted in a separate repository. For more information on ChunkVault-Lite, please visit the Valink Solutions website.

For support or issues with Teller-CLI, please visit the Teller-CLI GitHub repository.
