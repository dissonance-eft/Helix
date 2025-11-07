# Helix

Local-first automation runner that executes JSON manifests with a repeatable loop: **describe → build → validate → log**.

## Quick Start

### Windows

```powershell
cd core
dotnet new console --force
dotnet run --project . examples/yt_download_windows.json
```

### Linux

```bash
cd core
dotnet new console --force
dotnet run --project . examples/yt_download_linux.json
```

## Features

- Cross-platform shell command execution (Windows/Linux)
- File and directory validation
- Checksum generation (SHA256)
- Plain text logging under `/logs`

## Project Structure

```
Helix/
├── core/
│   ├── Program.cs          # Main runner
│   └── examples/           # Example manifests
├── docs/                   # Documentation
├── scripts/                # Helper scripts
└── tools/                  # Development tools
```

## License

Apache 2.0

