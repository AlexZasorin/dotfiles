{ pkgs, ... }: {
  environment.systemPackages = with pkgs; [
    # Applications
    discord
    filelight
    firefox
    google-chrome
    hydrus
    krita
    pavucontrol
    qbittorrent
    spotify
    vesktop
    vlc
    vscode
    wezterm

    # KDE specific
    kdePackages.kdeconnect-kde

    # Other graphical tools
    libnotify
    todoist-electron

    # hyprland stuff
    dolphin
    dunst
    hyprshot
    kdePackages.qt6ct
    kitty
    libsForQt5.qt5.qtwayland
    nwg-bar
    polkit-kde-agent
    rofi-wayland
    waybar
    wireplumber
    wofi
    xclip
    xdg-desktop-portal-hyprland
  ];

  # Font packages
  fonts.packages = with pkgs; [
    nerdfonts
    jetbrains-mono
    noto-fonts-cjk-sans
  ];
}