{pkgs, ...}: {
  # GRUB bootloader (UEFI). Imported by the graphical hosts via flake.nix.
  # The server (ceres) deliberately does NOT import this — it uses systemd-boot.
  boot.loader = {
    efi.canTouchEfiVariables = true;
    grub = {
      enable = true;
      device = "nodev";
      useOSProber = true;
      efiSupport = true;
      gfxmodeEfi = "2560x1440,1920x1080";
      default = "saved";
      theme = pkgs.stdenv.mkDerivation {
        pname = "grub2-solarized-dark";
        version = "daabc2c6d6179bd99f20bfc46d25f6433eecdd68";
        src = pkgs.fetchFromGitHub {
          owner = "bino-faata";
          repo = "grub2-solarized-dark";
          rev = "daabc2c6d6179bd99f20bfc46d25f6433eecdd68";
          sha256 = "1awbi6z8016l7vmlkwvhfaw0b5a5chjjqb26vl0swarfpb0d73ky";
        };
        installPhase = "cp -r . $out";
      };
    };
  };
}
