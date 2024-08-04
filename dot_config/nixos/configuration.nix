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
  ];

  nix.settings = {
    experimental-features = ["nix-command" "flakes"];
  };

  nix.nixPath = [
    "nixpkgs=flake:nixpkgs:/nix/var/nix/profiles/per-user/root/channels"
    "nixos-config=$HOME/.config/nixos"
    "/home/solyx/.nix-defexpr/channels"
  ];

  # Bootloader
  boot = {
    supportedFilesystems = ["ntfs"];
    loader = {
      efi = {
        canTouchEfiVariables = true;
      };
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
  };

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  networking.networkmanager.enable = true;
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.
  networking.firewall = {
    enable = true;
    allowedTCPPortRanges = [
      {
        from = 1714;
        to = 1764;
      } # KDE Connect
    ];
    allowedUDPPortRanges = [
      {
        from = 1714;
        to = 1764;
      } # KDE Connect
    ];
    extraCommands = ''iptables -t raw -A OUTPUT -p udp -m udp --dport 137 -j CT --helper netbios-ns'';
  };

  networking.nameservers = ["8.8.8.8" "8.8.4.4"];

  services.resolved = {
    enable = true;
    domains = ["~."];
    fallbackDns = ["8.8.8.8" "8.8.4.4"];
  };

  services.ivpn.enable = true;

  services.gnome.gnome-keyring.enable = true;

  # Set your time zone.
  time.timeZone = "America/Los_Angeles";
  time.hardwareClockInLocalTime = true;

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  i18n.extraLocaleSettings = {
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

  # Enable the X11 windowing system.
  services.xserver.enable = true;

  programs.xwayland.enable = true;

  # Enable the KDE Plasma Desktop Environment.
  # services.xserver.desktopManager.plasma5.enable = true;
  services.desktopManager.plasma6.enable = true;
  programs.hyprland = {
    enable = true;
    xwayland.enable = true;
  };

  services.atuin.enable = true;

  # Enable SDDM
  services.displayManager.sddm.enable = true;
  # services.displayManager.sddm.wayland.enable = true;

  # Enable XDG Portal?
  xdg.portal.enable = true;

  environment = {
    loginShellInit = ''
      dbus-update-activation-environment --systemd DISPLAY
      eval $(gnome-keyring-daemon --start --components=pkcs11,secrets,ssh) 1> /dev/null
    '';
    variables.EDITOR = "nvim";
    sessionVariables = {
      # hyprland
      NIXOS_OZONE_WL = "1";
    };
  };
  # Configure keymap in X11
  # services.xserver = {
  #   xkb.layout = "us";
  #   xkb.variant = "";
  #   # When moving to Wayland, make sure to port this configuration to run at the beginning of a Wayland session
  #   displayManager = {
  #     sessionCommands = ''
  #       eval $(${pkgs.gnome-keyring}/bin/gnome-keyring-daemon --start --components=pkcs11,secrets,ssh)
  #       export SSH_AUTH_SOCK };
  #     '';
  #   };
  # };

  # Enable CUPS to print documents.
  services.printing.enable = true;

  # Enable sound with pipewire.
  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  security.pam.services.sddm.enableGnomeKeyring = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    # If you want to use JACK applications, uncomment this
    #jack.enable = true;

    # use the example session manager (no others are packaged yet so this is enabled by default,
    # no need to redefine it in your config for now)
    #media-session.enable = true;
  };

  systemd.services.kanata = {
    enable = true;
    description = "run kanata";
    unitConfig = {
      type = "simple";
    };
    serviceConfig = {
      ExecStart = "${pkgs.kanata}/bin/kanata -d -c /home/solyx/.config/kanata/kanata.kbd";
      Restart = "always";
      RestartSec = 10;
      User = "root";
      Group = "root";
    };
    wantedBy = ["multi-user.target"];
  };

  systemd.services.noisetorch-init = {
    enable = true;
    description = "Initialize NoiseTorch";
    after = ["pipewire.service"];
    unitConfig = {
      type = "oneshot";
    };
    serviceConfig = {
      ExecStart = "${pkgs.noisetorch}/bin/noisetorch -i";
      # ExecStop = "${pkgs.noisetorch}/bin/noisetorch -u";
      Restart = "on-failure";
      RestartSec = 3;
      User = "solyx";
    };
    wantedBy = ["default.target"];
  };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.solyx = {
    isNormalUser = true;
    description = "solyx";
    extraGroups = ["networkmanager" "wheel"];
    packages = with pkgs; [
      asciiquarium
      atuin
      aws-sam-cli
      awscli2
      bottom
      broot
      chezmoi
      discord
      docker
      eslint_d
      eza
      fd
      filelight
      firefox
      fzf
      gh
      git
      gitui
      gnome-keyring
      google-chrome
      gsmartcontrol
      helix
      heroic
      htop
      hydrus
      ivpn
      ivpn-service
      jetbrains-toolbox
      jsonnet
      kanata
      kdePackages.kdeconnect-kde
      krita
      kubectl
      kubectx
      lazydocker
      lazygit
      libnotify
      luarocks
      neofetch
      nodejs_22
      papirus-icon-theme
      pavucontrol
      prettierd
      pnpm
      python312
      python312Packages.pip
      ripgrep
      slides
      spotify
      steam
      tmux
      todoist-electron
      unzip
      vesktop
      vscode
      yazi
      zellij
      zoxide
      zsh
      # hyprland stuff
      dolphin
      dunst
      hyprshot
      kdePackages.qt6ct
      kitty
      libsForQt5.qt5.qtwayland
      nwg-bar
      polkit-kde-agent
      rofi-wayland
      waybar
      wireplumber
      wofi
      xdg-desktop-portal-hyprland
    ];
  };

  programs = {
    zsh = {
      enable = true;
    };
    kdeconnect = {
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
    noisetorch = {
      enable = true;
    };
    steam = {
      enable = true;
      remotePlay.openFirewall = true;
      dedicatedServer.openFirewall = true;
      localNetworkGameTransfers.openFirewall = true;
    };
  };

  users.defaultUserShell = pkgs.zsh;

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    alejandra
    btop
    cargo
    cifs-utils
    clang
    curl
    dig
    ffmpeg
    gcc
    gnumake
    go
    inxi
    keychain
    neovim
    os-prober
    pciutils
    traceroute
    usbutils
    vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
    vlc
    wezterm
    wget
    which
    xclip
    zig
  ];

  fonts.packages = with pkgs; [
    nerdfonts
    jetbrains-mono
    noto-fonts-cjk-sans
  ];
  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "23.11"; # Did you read the comment?

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
