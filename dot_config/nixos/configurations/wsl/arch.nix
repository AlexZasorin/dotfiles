{ config, pkgs, ... }:
let
  base-packages = import ../../packages/base-packages.nix { inherit pkgs; };
  wsl-packages = import ../../packages/system-packages/wsl.nix { inherit pkgs; };
in {
  home = {
    username = "solyx";  # Replace with your username
    homeDirectory = "/home/solyx";  # Replace with your home directory
    stateVersion = "23.11";
    
    packages = base-packages.base-packages ++ wsl-packages.wsl-packages;
  };

  fonts.fontconfig.enable = true;

  # Program-specific configurations
  programs = {
    home-manager.enable = true;
    atuin.enable = true;


    # git = {
    #  enable = true;
    #  userName = "Your Name";
    #  userEmail = "your.email@example.com";
    #};
  };

  # Environment variables
  home.sessionVariables = {
    EDITOR = "nvim";
    TERM = "xterm-256color";
    LOCALE_ARCHIVE = "${pkgs.glibcLocales}/lib/locale/locale-archive";
  };
}
