{pkgs, inputs, ...}: {
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

    # Game Stuff
    prismlauncher
    inputs.dzgui-nix.packages.x86_64-linux.default

    # KDE specific
    kdePackages.kclock
    kdePackages.dolphin
    kdePackages.dolphin-plugins
    kdePackages.filelight
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
  ];
}
