{ config, pkgs, ... }:

{
  home = {
    username = "solyx";  # Replace with your username
    homeDirectory = "/home/solyx";  # Replace with your home directory
    stateVersion = "23.11";
    
    packages = with pkgs; [
      # Development
      git
      gitui
      vim
      neovim
      eza
      nodejs_22
      unzip
      go
      cargo
      python313

      # System tools
      htop
      ripgrep
      fd
      chezmoi
      
      # Network tools
      curl
      wget
      
      # Add more packages as needed
    ];
  };

  # Program-specific configurations
  programs = {
    home-manager.enable = true;
    
    # git = {
    #  enable = true;
    #  userName = "Your Name";
    #  userEmail = "your.email@example.com";
    #};
  };

  # Environment variables
  home.sessionVariables = {
    EDITOR = "nvim";
  };
}
