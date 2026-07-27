{
  pkgs,
  config,
  lib,
  ...
}: {
  networking.hostName = "deimos"; # Define your hostname.

  nix = {
    settings = {
      cores = 4;
      max-jobs = 8;
    };
  };

  boot.resumeDevice = "/dev/disk/by-uuid/00be8230-2406-4495-b77c-f14ca0ebae89";
  boot.kernelParams = ["mem_sleep_default=s2idle"];
  boot.kernelPackages = lib.mkIf (lib.versionOlder pkgs.linux.version "5.16") pkgs.linuxPackages_latest;

  hardware.cpu.amd.updateMicrocode = lib.mkDefault config.hardware.enableRedistributableFirmware;
  hardware.graphics = {
    enable = lib.mkDefault true;
    enable32Bit = lib.mkDefault true;
  };
  hardware.amdgpu.initrd.enable = lib.mkDefault true;

  services.xserver.videoDrivers = lib.mkDefault ["modesetting"];
  services.power-profiles-daemon.enable = false;

  # Touchpad support.
  services.libinput.enable = true;

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
    settings.Login = {
      HandleLidSwitch = "suspend-then-hibernate";
      HandlePowerKey = "suspend-then-hibernate";
      IdleAction = "suspend-then-hibernate";
      IdleActionSec = "10m";
    };
  };

  services.fstrim.enable = lib.mkDefault true;

  systemd.sleep.settings.Sleep = {
    HibernateDelaySec = "10m";
  };

  networking.networkmanager.wifi.powersave = false;

  # Uncomment if WiFi stops working after wake from sleep.
  # The sleep state change (s2idle) may fix this without needing a driver reload.
  # systemd.services.ath11k-resume = {
  #   enable = true;
  #   description = "Reload ath11k WiFi driver after wake from sleep";
  #   after = ["suspend-then-hibernate.target" "hibernate.target" "suspend.target"];
  #   wantedBy = ["suspend-then-hibernate.target" "hibernate.target" "suspend.target"];
  #   serviceConfig = {
  #     Type = "oneshot";
  #     RemainAfterExit = true;
  #     ExecStart = "${pkgs.kmod}/bin/modprobe -rv ath11k_pci";
  #     ExecStop = "${pkgs.kmod}/bin/modprobe -v ath11k_pci";
  #   };
  # };

  # TODO: set the paths you actually want backed up on deimos.
  services.restic.backups.b2.paths = [
    "/home/solyx"
  ];

  # Release this host was first installed on. Do not change (see NixOS manual).
  system.stateVersion = "23.11";
}
