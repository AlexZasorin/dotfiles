{pkgs, inputs, ...}: {
  environment.systemPackages = let
    neovim-pinned = inputs.nixpkgs-neovim.legacyPackages.${pkgs.system}.neovim;
    standardPackages = with pkgs; [
      # Development tools
      alejandra
      cmake
      eslint_d
      git
      gnumake
      gcc
      go
      lua5_1
      luarocks
      prettierd
      neovim-pinned

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
      killall
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
      lsof
      unixtools.netstat
      openssl
      traceroute

      # Version control
      gh
      gitui
      lazygit

      # Cloud & container tools
      docker
      docker-compose
      kubectl
      kubectx
      lazydocker

      # Other CLI tools
      asciiquarium
      dmidecode
      ffmpeg
      slides
      spicetify-cli
    ];
  in
    standardPackages;

  # Font packages
  fonts.packages = with pkgs; [
    nerd-fonts.jetbrains-mono
    noto-fonts-cjk-sans
    carlito
  ];
}
