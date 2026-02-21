{
  pkgs,
  config,
  ...
}: {
  # KDE Plasma Desktop Environment
  services.desktopManager.plasma6.enable = true;

  # SDDM Display Manager
  services.displayManager.sddm.enable = true;

  services.xserver.enable = true;

  # XDG Portal
  xdg.portal.enable = true;

  security.pam.services = {
    login = {
      kwallet.enable = true;
    };
  };
}
