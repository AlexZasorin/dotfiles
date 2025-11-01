{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Applications
    darktable
    discord
    kdePackages.filelight
    firefox
    hydrus
    krita
    libreoffice-qt6
    pavucontrol
    protonmail-desktop
    qbittorrent
    spotify
    vesktop
    vlc
    vscode
    wezterm

    # KDE specific
    kdePackages.kdeconnect-kde
    k4dirstat

    # Other graphical tools
    libnotify
    todoist-electron

    # hyprland stuff
    kdePackages.dolphin
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
