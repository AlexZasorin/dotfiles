{pkgs, inputs, ...}: {
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
      lua5_1
      luarocks
      prettierd
      neovim

      # Shell utilities
      android-tools
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
      yt-dlp
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
      rclone
      restic
      sops
      slides
      spicetify-cli
      vhs
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
