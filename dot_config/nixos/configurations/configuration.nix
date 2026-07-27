# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running ‘nixos-help’).
{
  config,
  pkgs,
  inputs,
  ...
}: {
  imports = [
    # Include the results of the hardware scan.
    ./hardware-configuration.nix
    inputs.sops-nix.nixosModules.sops
  ];

  zramSwap = {
    enable = true;
    priority = 100;
    algorithm = "zstd";
    memoryPercent = 50;
  };

  # Secrets
  sops = {
    defaultSopsFile = ../secrets/secrets.yaml;
    defaultSopsFormat = "yaml";

    age = {
      keyFile = "${config.users.users.solyx.home}/.config/sops/age/keys.txt";
      sshKeyPaths = [];
    };
    gnupg.sshKeyPaths = [];

    secrets = {
      anthropic_token = {
        owner = "solyx";
      };
      github_token = {
        owner = "solyx";
      };
    };

    templates."nix-access-tokens".content = ''
      access-tokens = ${config.sops.placeholder."github_token"}
    '';
  };

  nix = {
    settings = {
      experimental-features = ["nix-command" "flakes"];
    };

    extraOptions = ''
      !include ${config.sops.templates."nix-access-tokens".path}
    '';

    nixPath = [
      "nixpkgs=flake:nixpkgs:/nix/var/nix/profiles/per-user/root/channels"
      "nixos-config=$HOME/.config/nixos"
    ];
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # Bootloader config (GRUB) lives in ./grub.nix, imported per-host via flake.nix.
  boot = {
    supportedFilesystems = ["ntfs"];
  };

  virtualisation.docker.enable = true;

  networking = {
    nameservers = ["8.8.8.8" "8.8.4.4"];
    networkmanager.enable = true;
    firewall = {
      enable = true;
      extraCommands = ''iptables -t raw -A OUTPUT -p udp -m udp --dport 137 -j CT --helper netbios-ns'';
    };
  };

  services = {
    atuin.enable = true;
    ivpn.enable = true;
    resolved = {
      enable = true;
      settings = {
        Resolve.Domains = ["~."];
        Resolve.FallbackDNS = ["8.8.8.8" "8.8.4.4"];
      };
    };

    # Enable the OpenSSH daemon.
    openssh.enable = true;
  };

  # Set your time zone.
  time = {
    timeZone = "America/Los_Angeles";
    hardwareClockInLocalTime = true;
  };

  # Select internationalisation properties.
  i18n = {
    # Select internationalisation properties.
    defaultLocale = "en_US.UTF-8";

    extraLocaleSettings = {
      LC_ADDRESS = "en_US.UTF-8";
      LC_IDENTIFICATION = "en_US.UTF-8";
      LC_MEASUREMENT = "en_US.UTF-8";
      LC_MONETARY = "en_US.UTF-8";
      LC_NAME = "en_US.UTF-8";
      LC_NUMERIC = "en_US.UTF-8";
      LC_PAPER = "en_US.UTF-8";
      LC_TELEPHONE = "en_US.UTF-8";
      LC_TIME = "en_US.UTF-8";
    };
  };

  environment = {
    variables = {
      EDITOR = "nvim";
      NH_OS_FLAKE = "${config.users.users.solyx.home}/.config/nixos";
      NIXOS_INSTALL_BOOTLOADER = "true";
    };
  };

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users = {
    defaultUserShell = pkgs.zsh;
    users.solyx = {
      isNormalUser = true;
      description = "solyx";
      extraGroups = ["networkmanager" "wheel" "docker"];
    };
  };

  programs = {
    nh = {
      enable = true;
      clean.enable = true;
      clean.extraArgs = "--keep-since 4d --keep 3";
      flake = "${config.users.users.solyx.home}/.config/nixos";
    };
    zsh = {
      enable = true;
      loginShellInit = ''
        export GITHUB_TOKEN="$(cat ${config.sops.secrets.github_token.path})";
        export ANTHROPIC_API_KEY="$(cat ${config.sops.secrets.anthropic_token.path})";
      '';
    };
    # Base nix-ld libraries. Graphical hosts add GUI/electron libs in graphical.nix.
    nix-ld = {
      enable = true;
      libraries = with pkgs; [
        stdenv.cc.cc.lib
      ];
    };
    ssh = {
      enableAskPassword = true;
      startAgent = true;
      extraConfig = "AddressFamily inet";
    };
  };

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [];

  # NOTE: system.stateVersion is intentionally NOT set here. It must be pinned
  # per-host to the release each machine was first installed on, so it lives in
  # the host modules (desktop.nix, laptop.nix, server.nix) and the `default`
  # output in flake.nix.
}
