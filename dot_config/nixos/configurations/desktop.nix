{ pkgs, ... }: {
  networking.hostName = "phobos"; # Define your hostname.

  # Desktop monitor layout (X11/SDDM greeter)
  services.xserver.displayManager.setupCommands = ''
    /run/current-system/sw/bin/xrandr --output HDMI-0 --auto
    /run/current-system/sw/bin/xrandr --output DP-2 --primary --left-of HDMI-0
    /run/current-system/sw/bin/xrandr --output HDMI-1 --left-of DP-2
  '';

  fileSystems."/mnt/share" = {
    device = "//192.168.1.160/smb_alex";
    fsType = "cifs";
    options = [
      "x-systemd.automount"
      "noauto"
      "x-systemd.idle-timeout=60"
      "x-systemd.device-timeout=5s"
      "x-systemd.mount-timeout=5s"
      "credentials=/etc/nixos/smb-secrets"
      "uid=1000"
      "gid=100"
    ];
  };

  # Hytale friend join (dynamic UDP ports)
  networking.firewall.allowedUDPPortRanges = [
    {
      from = 40000;
      to = 50000;
    }
  ];

  programs.steam.enable = true;
  programs.steam.gamescopeSession.enable = true;
  
  programs.gamemode.enable = true;

  services.flatpak.enable = true;

  virtualisation = {
    docker = {
      enable = true;
    };
  };
}
