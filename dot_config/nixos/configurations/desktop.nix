{pkgs, ...}: {
  networking.hostName = "phobos"; # Define your hostname.

  nix = {
    settings = {
      cores = 8;
      max-jobs = 16;
    };
  };

  environment.systemPackages = with pkgs; [
    kdePackages.krohnkite
  ];

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

  # Keep nosuid/nodev, allow exec.
  environment.etc."udisks2/mount_options.conf".text = ''
    [UUID=877d2dc0-81ca-44fa-a5bb-0353d59a9400]
    defaults=noatime,nosuid,nodev,exec
  '';

  # Hytale friend join (dynamic UDP ports)
  networking.firewall.allowedUDPPortRanges = [
    {
      from = 40000;
      to = 50000;
    }
  ];

  # TODO: set the paths you actually want backed up on phobos.
  services.restic.backups.b2.paths = [
    "/home/solyx"
  ];

  programs.steam.enable = true;
  programs.steam.gamescopeSession.enable = true;

  programs.gamemode.enable = true;

  services.flatpak.enable = true;

  programs.obs-studio = {
    enable = true;
    package = pkgs.obs-studio.override {
      cudaSupport = true;
    };
  };

  # Release this host was first installed on. Do not change (see NixOS manual).
  system.stateVersion = "23.11";
}
