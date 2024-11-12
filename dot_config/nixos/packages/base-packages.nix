{ pkgs, ... }: {
  environment.systemPackages = with pkgs; [
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
    neovim
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
    kubectl
    kubectx
    lazydocker

    # Other CLI tools
    asciiquarium
    ffmpeg
    slides
  ];

  # Font packages
  fonts.packages = with pkgs; [
    nerdfonts
    jetbrains-mono
    noto-fonts-cjk-sans
  ];
}
