{
  pkgs,
  config,
  ...
}: {
  # Config shared by hosts with a graphical session (desktop, laptop).
  # Not imported by the server.

  # olm is only pulled in by nheko (Matrix client, a graphical package).
  # TODO: Look into removing once nheko no longer needs olm-3.2.16.
  nixpkgs.config.permittedInsecurePackages = [
    "olm-3.2.16"
  ];

  # KDE Plasma Desktop Environment
  services.desktopManager.plasma6.enable = true;

  # SDDM Display Manager
  services.displayManager.sddm.enable = true;

  services.xserver.enable = true;

  # XDG Portal
  xdg.portal.enable = true;

  # Enable CUPS to print documents.
  services.printing.enable = true;

  # Removable-media automounting for file managers.
  services.gvfs.enable = true;
  services.udisks2.enable = true;
  services.devmon.enable = true;
  systemd.user.services.devmon.unitConfig.ConditionUser = "solyx";

  # Sound with pipewire.
  services.pulseaudio.enable = false;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  i18n.inputMethod = {
    enable = true;
    type = "fcitx5";
    fcitx5.addons = with pkgs; [fcitx5-m17n fcitx5-mozc];
  };

  security = {
    rtkit.enable = true;
    pam.services = {
      login.kwallet.enable = true;
      sddm.enableGnomeKeyring = true;
    };
  };

  programs.kdeconnect.enable = true;
  programs.noisetorch.enable = true;

  # Firewall ports for KDE Connect.
  networking.firewall = {
    allowedTCPPortRanges = [
      {
        from = 1714;
        to = 1764;
      }
    ];
    allowedUDPPortRanges = [
      {
        from = 1714;
        to = 1764;
      }
    ];
  };

  # Userspace libraries for nix-ld (GUI/electron apps). Merged with the base
  # nix-ld config in configuration.nix.
  programs.nix-ld.libraries = with pkgs; [
    alsa-lib
    at-spi2-core
    cairo
    cups
    dbus
    expat
    fontconfig
    freetype
    gdk-pixbuf
    glib
    gtk3
    icu.dev
    libdrm
    libgbm
    libxkbcommon
    nspr
    pango
    libX11
    libXcomposite
    libXcursor
    libXdamage
    libXext
    libXfixes
    libXi
    libXrandr
    libXrender
    libxcb
    xcbutilwm
    xcbutilimage
    xcbutilkeysyms
    xcbutilrenderutil
    xcb-util-cursor
    harfbuzz
    icu
    sqlite
    libxslt
    lcms2
    woff2
    libevent
    libopus
    libgcrypt
    libgpg-error
    libwebp
    harfbuzzFull
    libepoxy
    libjpeg_turbo
    libpng
    enchant
    libsecret
    libtasn1
    hyphen
    libpsl
    nghttp2.lib
    libglvnd
    libgudev
    libevdev
    libffi
    pcre2
    json-glib
    gnutls
    openssl
  ];

  # Keyboard remapping daemon.
  systemd.services.kanata = {
    enable = true;
    description = "run kanata";
    serviceConfig = {
      ExecStart = "${pkgs.kanata}/bin/kanata -d -c ${config.users.users.solyx.home}/.config/kanata/kanata.kbd";
      Restart = "always";
      RestartSec = 10;
      User = "root";
      Group = "root";
      Type = "simple";
    };
    wantedBy = ["multi-user.target"];
  };
}
