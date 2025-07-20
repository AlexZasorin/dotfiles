{
  pkgs,
  config,
  lib,
  ...
}: {
  networking.hostName = "deimos"; # Define your hostname.

  swapDevices = [
    {device = "/dev/disk/by-uuid/00be8230-2406-4495-b77c-f14ca0ebae89";}
  ];
  boot.resumeDevice = "/dev/disk/by-uuid/00be8230-2406-4495-b77c-f14ca0ebae89";
  boot.kernelParams = ["mem_sleep_default=deep"];
  boot.kernelPackages = lib.mkIf (lib.versionOlder pkgs.linux.version "5.16") pkgs.linuxPackages_latest;

  hardware.bluetooth.enable = true;
  hardware.bluetooth.powerOnBoot = true;
  hardware.cpu.amd.updateMicrocode = lib.mkDefault config.hardware.enableRedistributableFirmware;
  hardware.graphics = {
    enable = lib.mkDefault true;
    enable32Bit = lib.mkDefault true;
  };
  hardware.amdgpu.initrd.enable = lib.mkDefault true;

  services.xserver.videoDrivers = lib.mkDefault [ "modesetting" ];
  services.power-profiles-daemon.enable = false;

  services.tlp = {
    enable = true;
    settings = {
      CPU_BOOST_ON_BAT = 0;
      CPU_SCALING_GOVERNOR_ON_BATTERY = "powersave";
      START_CHARGE_THRESH_BAT0 = 90;
      STOP_CHARGE_THRESH_BAT0 = 97;
      RUNTIME_PM_ON_BAT = "auto";
    };
  };

  services.logind = {
    lidSwitch = "suspend-then-hibernate";
    extraConfig = ''
      HandlePowerKey=suspend-then-hibernate
      IdleAction=suspend-then-hibernate
      IdleActionSec=10m
    '';
  };

  services.fstrim.enable = lib.mkDefault true;

  systemd.sleep.extraConfig = "HibernateDelaySec=10m";
  networking.networkmanager.wifi.powersave = false;

  systemd.services.ath11k-resume = {
    enable = true;
    description = "Resume";
    after = ["suspend-then-hibernate.target"];
    wantedBy = ["suspend-then-hibernate.target"];
    serviceConfig = {
      Type = "oneshot";
      ExecStart = [
        "${pkgs.kmod}/bin/modprobe -rv ath11k_pci"
        "${pkgs.kmod}/bin/modprobe -v ath11k_pci"
      ];
    };
  };

  virtualisation = {
    docker = {
      enable = true;
    };
  };
}
