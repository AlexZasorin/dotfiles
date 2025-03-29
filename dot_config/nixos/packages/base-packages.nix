{
  pkgs,
  pkgs-neovim,
  ...
}: {
  environment.systemPackages = let
    standardPackages = with pkgs; [
      # Development tools
      alejandra
      cmake
      eslint_d
      git
      gnumake
      gcc
      go
      luarocks
      prettierd

      # Shell utilities
      atuin
      bottom
      btop
      chezmoi
      curl
      eza
      fd
      fzf
      htop
      neofetch
      ripgrep
      smartcat
      tmux
      unzip
      vim
      wget
      which
      zellij
      zoxide
      zsh

      # Network tools
      dig
      ivpn
      ivpn-service
      traceroute

      # Version control
      gh
      gitui
      lazygit

      # Cloud & container tools
      aws-sam-cli
      docker
      docker-compose
      kubectl
      kubectx
      lazydocker

      # Other CLI tools
      asciiquarium
      ffmpeg
      slides
    ];
    neovimPackages = with pkgs-neovim; [
      neovim
    ];
  in
    standardPackages ++ neovimPackages;

  # Font packages
  fonts.packages = with pkgs; [
    nerd-fonts.jetbrains-mono
    noto-fonts-cjk-sans
  ];
}
