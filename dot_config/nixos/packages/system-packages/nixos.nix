{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    cifs-utils
    inxi
    keychain
    os-prober
    pciutils
    usbutils
    wl-clipboard
  ];
}
