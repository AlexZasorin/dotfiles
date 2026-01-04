# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a chezmoi-managed dotfiles repository that includes NixOS system configurations. It manages dotfiles across multiple systems (desktop, laptop, server) and operating systems (NixOS on Linux, macOS with Homebrew).

## Architecture

### Chezmoi Structure

- **Source directory**: `/Users/azasorin/.local/share/chezmoi` (current working directory)
- **Target directory**: User's home directory (`~`)
- **File naming conventions**:
  - `dot_` prefix → `.` (e.g., `dot_config` → `~/.config`)
  - `private_` prefix → file with restricted permissions
  - `.tmpl` suffix → template files processed with Go templating
  - `executable_` prefix → file will be made executable

### NixOS Configuration

The NixOS configuration is located in `dot_config/nixos/` and uses a flake-based modular structure:

**Flake outputs** (`dot_config/nixos/flake.nix`):
- `desktop` - Full desktop configuration (hostname: phobos)
- `laptop` - Laptop configuration (hostname: deimos)
- `server` - Minimal server configuration (hostname: ceres)
- `default` - Fallback configuration

**Module organization**:
- `configurations/` - Host-specific and base system configuration
  - `configuration.nix` - Base configuration with bootloader, networking, users, services, sops-nix secrets
  - `desktop.nix` - Desktop-specific settings (Steam, SMB mounts)
  - `laptop.nix` - Laptop-specific settings
  - `server.nix` - Server-specific settings (minimal, headless)
  - `graphical.nix` - Graphical environment settings
- `packages/` - Package collections
  - `default.nix` - Imports all package modules
  - `base-packages.nix` - Core CLI tools, fonts, shell utilities
  - `development-packages.nix` - Development tools
  - `graphical-packages.nix` - GUI applications
  - `gaming.nix` - Gaming-related packages
  - `system-packages/nixos.nix` - NixOS-specific system packages
- `graphics/` - Graphics driver configurations
  - `nvidia.nix` - NVIDIA driver configuration
  - `radeon.nix` - AMD Radeon driver configuration
- `secrets/` - sops-nix encrypted secrets
  - `secrets.yaml` - Encrypted secrets file (contains github_token, anthropic_token)

### Key Configuration Details

**Secrets Management**:
- Uses sops-nix for encrypted secrets
- Age key location: `/home/solyx/.config/sops/age/keys.txt`
- Secrets are exposed as environment variables in `configuration.nix`:
  - `GITHUB_TOKEN` - from `sops.secrets.github_token`
  - `ANTHROPIC_API_KEY` - from `sops.secrets.anthropic_token`

**User Configuration**:
- Primary user: `solyx`
- Default shell: `zsh`
- User groups: `networkmanager`, `wheel`, `docker`

**System Services**:
- Desktop environment: KDE Plasma 6 with SDDM (Wayland)
- Custom systemd services:
  - `kanata` - Keyboard remapping daemon
  - `noisetorch-init` - Noise suppression initialization

## Common Commands

### Chezmoi Operations

```bash
# Apply dotfiles from source to home directory
chezmoi apply

# Edit a file and apply changes immediately
chezmoi edit --apply <file>

# Show differences between source and target
chezmoi diff

# Update dotfiles from source directory
chezmoi re-add

# Execute in source directory
chezmoi cd
```

### NixOS Rebuild Workflow

The repository includes a custom rebuild script at `scripts/nix/rebuild.sh.tmpl` that:
1. Edits the configuration file with chezmoi
2. Auto-formats with alejandra
3. Rebuilds the system
4. Commits changes on successful build
5. Cleans up old generations

```bash
# Rebuild NixOS system (uses hostname detection)
~/scripts/nix/rebuild.sh

# Rebuild with specific configuration
~/scripts/nix/rebuild.sh configurations/configuration.nix

# Manual rebuild commands (alternative to script)
sudo nixos-rebuild switch --flake ~/.config/nixos#desktop   # for phobos
sudo nixos-rebuild switch --flake ~/.config/nixos#laptop   # for deimos
sudo nixos-rebuild switch --flake ~/.config/nixos#server   # for ceres
sudo nixos-rebuild switch --flake ~/.config/nixos#default  # for other hosts

# Test configuration without switching
sudo nixos-rebuild test --flake ~/.config/nixos#<hostname>

# Build without activating
sudo nixos-rebuild build --flake ~/.config/nixos#<hostname>

# Format Nix files
alejandra .

# Clean up old generations
~/scripts/nix/cleanup.sh  # deletes generations older than 15 days
```

### Working with Secrets

```bash
# Edit encrypted secrets (requires age key)
sops dot_config/nixos/secrets/secrets.yaml

# Update secrets file
cd dot_config/nixos && sops updatekeys secrets/secrets.yaml
```

## Development Workflow

1. **Modifying dotfiles**: Edit files in the source directory (current working directory), then run `chezmoi apply` to deploy to home directory.

2. **Modifying NixOS configuration**:
   - Edit files in `dot_config/nixos/`
   - Run `~/scripts/nix/rebuild.sh` to format, rebuild, and commit
   - The script will only commit if the rebuild succeeds

3. **Adding new packages**:
   - System packages: Add to appropriate file in `dot_config/nixos/packages/`
   - User-specific packages: Add to user packages in configuration files

4. **Adding new hosts**:
   - Create new configuration file in `dot_config/nixos/configurations/<hostname>.nix`
   - Add new nixosConfiguration in `dot_config/nixos/flake.nix`
   - Update `scripts/nix/rebuild.sh.tmpl` with new hostname condition

5. **Template files**: Use chezmoi's Go template syntax. Available variables include:
   - `.chezmoi.hostname` - Current hostname
   - `.email` - Email address (prompted on first run)

## File Organization

- `dot_config/` - Application configurations (deployed to `~/.config/`)
- `dot_oh-my-zsh/` - Oh My Zsh with custom plugins and themes
- `private_dot_ssh/` - SSH configuration (restricted permissions)
- `scripts/` - Utility scripts
  - `nix/` - NixOS-specific scripts
  - `zsh/` - Shell helper functions

## Important Notes

- This repository manages multiple machines with different configurations (desktop gaming rig, laptop, headless server)
- NixOS configuration uses unstable channel via flakes
- The rebuild script automatically commits successful builds with generation metadata
- Secrets are encrypted with sops-nix and should never be committed in plaintext
- Alejandra is used for Nix code formatting (enforced by rebuild script)
