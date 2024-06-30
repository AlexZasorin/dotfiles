{config, ...}: {
  swapDevices = [
    {device = "/dev/disk/by-uuid/bfe6cd91-9b4e-48eb-b76c-641df97f4286";}
  ];
  boot.resumeDevice = "/dev/disk/by-uuid/bfe6cd91-9b4e-48eb-b76c-641df97f4286";
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
}
