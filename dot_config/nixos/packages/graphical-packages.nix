{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Applications
    audacity
    darktable
    discord
    ente-desktop
    firefox
    ivpn-ui
    krita
    libreoffice-qt6
    nheko
    pavucontrol
    protonmail-desktop
    qbittorrent
    rawtherapee
    shotcut
    signal-desktop
    spotify
    vesktop
    vlc
    vscode
    wezterm
    zoom-us

    # Game Stuff
    prismlauncher

    # KDE specific
    kdePackages.dolphin
    kdePackages.dolphin-plugins
    kdePackages.filelight
    kdePackages.kclock
    kdePackages.kdeconnect-kde
    kdePackages.kdegraphics-thumbnailers
    kdePackages.kdenlive
    kdePackages.kimageformats
    kdePackages.kio
    kdePackages.kio-extras
    kdePackages.kwallet-pam
    kdePackages.partitionmanager
    qdirstat

    # Other graphical tools
    gtk3
    libnotify
    todoist-electron
    wmctrl
    xclip
  ];
}
