{pkgs, ...}: {
  environment.systemPackages = let
    standardPackages = with pkgs; [
      # Development tools
      alejandra
      cmake
      eslint_d
      gcc
      git
      gnumake
      go
      jq
      jujutsu
      lua5_1
      luarocks
      lua51Packages.tree-sitter-cli
      neovim
      pkg-config
      prettierd
      zenity

      # Shell utilities
      android-tools
      atuin
      bitwarden-cli
      bottom
      btop
      chezmoi
      curl
      efibootmgr
      eza
      fastfetch
      fd
      fzf
      htop
      killall
      miniupnpc
      ripgrep
      smartcat
      sops
      tmux
      unzip
      wget
      which
      yt-dlp
      zellij
      zoxide

      # Network tools
      dig
      inetutils
      ivpn
      ivpn-service
      lsof
      openssl
      traceroute
      unixtools.netstat

      # Version control
      gh
      gitui
      lazygit

      # Cloud & container tools
      docker-compose
      kubectl
      kubectx
      lazydocker

      # Other CLI tools
      asciiquarium
      dmidecode
      ffmpeg
      hdparm
      parted
      rclone
      restic
      slides
      smartmontools
      spicetify-cli
      vhs
    ];
  in
    standardPackages;

  # Font packages
  fonts.packages = with pkgs; [
    carlito
    nerd-fonts.jetbrains-mono
    noto-fonts-cjk-sans
  ];
}
