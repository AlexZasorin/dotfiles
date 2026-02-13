{
  pkgs,
  config,
  ...
}: {
  networking.hostName = "phobos"; # Define your hostname.

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
