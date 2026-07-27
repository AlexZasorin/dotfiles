# ceres — headless server. Shares the universal base (configuration.nix) and
# bluetooth.nix via flake.nix; only server-specific config lives here.
{config, ...}: {
  # Bootloader (systemd-boot; the server does not use GRUB).
  boot = {
    initrd.kernelModules = ["xhci_pci" "usb_storage" "uas" "sd_mod"];
    loader = {
      systemd-boot.enable = true;
      efi.canTouchEfiVariables = true;
    };
  };

  networking = {
    hostName = "ceres";
    wireless.enable = true; # Enables wireless support via wpa_supplicant.
  };

  # Headless console.
  environment.variables.TERM = "xterm-256color";

  services = {
    cron = {
      enable = true;
      systemCronJobs = [
        "*/5 * * * *  solyx  ${config.users.users.solyx.home}/Repos/postpwn/deployment/deploy.sh >> /home/solyx/Repos/postpwn/deployment/deploy.log 2>&1"
      ];
    };
    # Configure keymap in X11
    xserver.xkb = {
      layout = "us";
      variant = "";
    };
    zwave-js = {
      enable = true;
      serialPort = "/dev/serial/by-id/usb-Zooz_800_Z-Wave_Stick_533D004242-if00";
      secretsConfigFile = "${config.users.users.solyx.home}/zwave-js.json";
    };
  };

  # Release this host was first installed on. Do not change (see NixOS manual).
  system.stateVersion = "24.05";
}
