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
  - `configuration.nix` - Base configuration shared by every host: sops-nix secrets, nix settings, networking, docker, openssh, zram, `nh`, zsh, nix-ld, user `solyx`. It imports `hardware-configuration.nix`, which is generated per host and is not in this repo.
  - `grub.nix` - GRUB (UEFI) bootloader. Desktop, laptop and `default` import it. The server uses systemd-boot instead.
  - `graphical.nix` - KDE Plasma 6, SDDM, kanata and other desktop-session settings. Desktop and laptop import it.
  - `bluetooth.nix` - Bluetooth. Laptop and server import it.
  - `restic.nix` - Restic backup to Backblaze B2. Desktop and laptop import it.
  - `desktop.nix` - Desktop-specific settings (Steam, gamescope, flatpak, SMB mounts)
  - `laptop.nix` - Laptop-specific settings (flatpak)
  - `server.nix` - Server-specific settings (headless, port 8123 for Home Assistant)
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
  - `secrets.yaml` - Encrypted secrets file. Keys: `anthropic_token`, `github_token`, `restic_password`, `hephaestus.credentials` (not referenced by any module)

### Key Configuration Details

**Secrets Management**:

- Uses sops-nix for encrypted secrets. The age key is at `/home/solyx/.config/sops/age/keys.txt`, and sops-nix decrypts into `/run/secrets/` at boot. All secrets are owned by `solyx`.
- `github_token` and `anthropic_token` are exported as `GITHUB_TOKEN` and `ANTHROPIC_API_KEY` in `programs.zsh.loginShellInit`, so they exist only in zsh login shells.
- `github_token` is also written into the nix `access-tokens` setting through a sops template.
- `restic_password` is the restic repository password (see Backups).

**User Configuration**:

- Primary user: `solyx`
- Default shell: `zsh`
- User groups: `networkmanager`, `wheel`, `docker`

**System Services**:

- Desktop and laptop (`graphical.nix`): KDE Plasma 6 with SDDM, and a `kanata` systemd service for keyboard remapping.
- Server (`server.nix`): headless. Opens port 8123 for Home Assistant.
- All hosts (`configuration.nix`): openssh, docker, atuin, ivpn, systemd-resolved.

**Backups** (`configurations/restic.nix`):

- Restic to Backblaze B2, imported by desktop and laptop. Each host backs up `/home/solyx` to its own prefix in the bucket, named after the hostname.
- Runs daily with a random delay of up to 1 hour. Prune keeps 7 daily, 4 weekly and 6 monthly snapshots.
- The repository password comes from the sops secret `restic_password`.
- The bucket name is still the placeholder `CHANGE_ME_BUCKET`.

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

Rebuilds use `nh`. The `programs.nh` block in `configurations/configuration.nix` enables it and sets `NH_OS_FLAKE` to `~/.config/nixos`. The flake outputs are named `desktop`, `laptop`, `server` and `default`, not after the hostnames, so select the output with `-H`.

```bash
# Rebuild and switch
nh os switch ~/.config/nixos -H desktop   # phobos
nh os switch ~/.config/nixos -H laptop    # deimos
nh os switch ~/.config/nixos -H server    # ceres
nh os switch ~/.config/nixos -H default   # other hosts

# NH_OS_FLAKE is set, so the path can be omitted
nh os switch -H server

# Test configuration without switching
nh os test ~/.config/nixos -H <output>

# Build without activating
nh os build ~/.config/nixos -H <output>

# Format Nix files
alejandra .

# Clean up old generations (programs.nh.clean runs the same command on a timer)
nh clean all --keep-since 4d --keep 3
```

### Working with Secrets

`dot_config/nixos/secrets/secrets.yaml` is encrypted with sops-nix. The user edits it. Do not decrypt it, do not run `sops` on it, and do not read the age key or any file under `/run/secrets/`.

## Development Workflow

1. **Modifying dotfiles**: Edit files in the source directory (current working directory), then run `chezmoi apply` to deploy to home directory.

2. **Modifying NixOS configuration**:
   - Edit files in `dot_config/nixos/`, then run `chezmoi apply`
   - Run `alejandra .` in `dot_config/nixos/`, then `nh os switch ~/.config/nixos -H <output>`
   - Commit after the rebuild succeeds

3. **Adding new packages**:
   - System packages: Add to appropriate file in `dot_config/nixos/packages/`
   - User-specific packages: Add to user packages in configuration files

4. **Adding new hosts**:
   - Create new configuration file in `dot_config/nixos/configurations/<hostname>.nix`
   - Add new nixosConfiguration in `dot_config/nixos/flake.nix`

5. **Template files**: Use chezmoi's Go template syntax. Available variables include:
   - `.chezmoi.hostname` - Current hostname
   - `.email` - Email address (prompted on first run, used by `dot_gitconfig.tmpl`)

## File Organization

- `dot_config/` - Application configurations (deployed to `~/.config/`)
- `dot_oh-my-zsh/` - Oh My Zsh with custom plugins and themes
- `private_dot_ssh/` - SSH configuration (restricted permissions)
- `scripts/` - Utility scripts
  - `zsh/` - Shell helper functions

## Important Notes

- This repository manages multiple machines with different configurations (desktop gaming rig, laptop, headless server)
- NixOS configuration uses unstable channel via flakes
- Secrets are encrypted with sops-nix and should never be committed in plaintext
- Alejandra is used for Nix code formatting
