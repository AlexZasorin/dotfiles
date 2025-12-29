{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Applications
    audacity
    bottles
    darktable
    discord
    firefox
    hydrus
    ivpn-ui
    krita
    libreoffice-qt6
    megasync
    nheko
    obsidian
    pavucontrol
    protonmail-desktop
    qbittorrent
    rawtherapee
    shotcut
    spotify
    vesktop
    vlc
    vscode
    wezterm

    # KDE specific
    kdePackages.dolphin
    kdePackages.dolphin-plugins
    kdePackages.filelight
    kdePackages.kio
    kdePackages.kio-extras
    kdePackages.kdegraphics-thumbnailers
    kdePackages.kimageformats
    kdePackages.kdeconnect-kde
    kdePackages.kdenlive
    kdePackages.kwallet-pam
    kdePackages.partitionmanager
    qdirstat

    # Other graphical tools
    libnotify
    todoist-electron

    # hyprland stuff
    dunst
    hyprshot
    kdePackages.qt6ct
    kitty
    libsForQt5.qt5.qtwayland
    nwg-bar
    kdePackages.polkit-kde-agent-1
    rofi
    waybar
    wireplumber
    wofi
    xclip
    xdg-desktop-portal-hyprland
  ];
}
