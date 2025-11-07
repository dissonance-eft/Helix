# Helix (Demo)

Local-first automation runner that executes small JSON manifests with a repeatable loop:

**describe → build → validate → log**.

## Features

- Runs shell commands locally (Windows/Linux)
- Simple validation (file/dir exists)
- Checksums for files or directories
- Plain log files under `/logs`

## Quick Start (Windows)

```powershell
cd core
dotnet new console --force
dotnet run --project . examples/yt_download_windows.json
```
