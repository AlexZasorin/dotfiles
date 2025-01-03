{pkgs, ...}: {
  imports = [
    ./base-packages.nix
    ./graphical-packages.nix
    ./development-packages.nix
  ];
}
