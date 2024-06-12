#!/bin/sh

# Ensure the target directory exists
sudo mkdir -p /etc/nixos

# Copy configuration files to /etc/nixos
sudo cp $HOME/.local/share/chezmoi/nixos/configuration.nix /etc/nixos/configuration.nix
sudo cp $HOME/.local/share/chezmoi/nixos/flake.nix /etc/nixos/flake.nix
sudo cp $HOME/.local/share/chezmoi/nixos/flake.lock /etc/nixos/flake.lock

echo "Successfully copied Nix configuration files"
