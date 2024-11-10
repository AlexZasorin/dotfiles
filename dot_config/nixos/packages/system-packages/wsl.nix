{ pkgs, ... }: {
  wsl-packages = with pkgs; [
    openssh
    zsh
    powerline-fonts
    (nerdfonts.override { fonts = [ "Meslo" ]; })
  ];
}

