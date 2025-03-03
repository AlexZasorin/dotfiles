{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    wslu
  ];
}
