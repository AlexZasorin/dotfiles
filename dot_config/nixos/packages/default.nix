{ pkgs, ... }: {
let
  base-packages = import ./base-packages.nix { inherit pkgs; };
  graphical-packages = import ./graphical-packages.nix { inherit pkgs; };
  development-packages = import ./development-packages.nix { inherit pkgs; };
in {
  environment.systemPackages = base-packages.base-packages ++ graphical-packages.graphical-packages ++ development-packages.development-packages;
}
