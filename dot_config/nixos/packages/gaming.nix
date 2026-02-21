{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    mangohud
    protonup-qt
  ];

  environment.sessionVariables = {
    STEAM_EXTRA_COMPAT_TOOLS_PATHS = "\${HOME}/.steam/root/compatibilitytools.d";
  };
}
