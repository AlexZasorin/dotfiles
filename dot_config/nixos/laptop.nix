{config, ...}: {
  swapDevices = [
    {device = "/dev/disk/by-uuid/00be8230-2406-4495-b77c-f14ca0ebae89";}
  ];
  boot.resumeDevice = "/dev/disk/by-uuid/00be8230-2406-4495-b77c-f14ca0ebae89";
  boot.kernelParams = ["mem_sleep_default=deep"];

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
  systemd.sleep.extraConfig = "HibernateDelaySec=30s";
  networking.networkmanager.wifi.powersave = false;
}