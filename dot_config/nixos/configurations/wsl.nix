{
  config,
  pkgs,
  inputs,
  ...
}: {
  nix.settings = {
    experimental-features = ["nix-command" "flakes"];
  };

  nix.nixPath = [
    "nixpkgs=flake:nixpkgs:/nix/var/nix/profiles/per-user/root/channels"
  ];

  wsl.enable = true;
  wsl.defaultUser = "solyx";
  users.users.solyx = {
    isNormalUser = true;
    extraGroups = ["wheel"];
  };

  services.atuin.enable = true;

  environment = {
    variables.EDITOR = "nvim";
  };

  programs = {
    zsh = {
      enable = true;
    };
    nix-ld = {
      enable = true;
      libraries = with pkgs; [
      ];
    };
    ssh = {
      enableAskPassword = true;
      startAgent = true;
      extraConfig = "AddressFamily inet";
    };
  };

  users.defaultUserShell = pkgs.zsh;

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [];

  system.stateVersion = "24.05";

  system.autoUpgrade = {
    enable = true;
    flake = inputs.self.outPath;
    flags = [
      "--update-input"
      "nixpkgs"
      "-L" # print build logs
    ];
    dates = "02:00";
    randomizedDelaySec = "45min";
  };
}
