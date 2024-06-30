{
  pkgs,
  config,
  ...
}: {
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

  systemd.sleep.extraConfig = "HibernateDelaySec=10m";
  networking.networkmanager.wifi.powersave = false;

  # systemd.services.ath11k-suspend = {
  #   description = "Suspend";
  #   before = ["suspend-then-hibernate.target"];
  #   wantedBy = ["suspend-then-hibernate.target"];
  #   serviceConfig = {
  #     Type = "oneshot";
  #     ExecStart = "${pkgs.kmod}/bin/rmmod ath11k_pci";
  #   };
  # };

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
}
