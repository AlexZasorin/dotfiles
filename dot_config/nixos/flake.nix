{
  description = "Nixos config flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    nixos-wsl.url = "github:nix-community/NixOS-WSL/main";
  };

  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config = {
        allowUnfree = true;
      };
    };
  in {
    nixosConfigurations = {
      desktop = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./packages/gaming.nix
          ./graphics/nvidia.nix
          ./configurations/configuration.nix
          ./configurations/desktop.nix
          ./configurations/graphical.nix
          ./secrets.nix
        ];
      };

      laptop = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./configurations/configuration.nix
          ./configurations/laptop.nix
          ./secrets.nix
        ];
      };

        ];
      };

      server = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        system = "x86_64-linux";
        modules = [
          ./packages/base-packages.nix
          ./packages/development-packages.nix
          ./configurations/server.nix
          ./secrets.nix
        ];
      };

      default = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./configurations/configuration.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
    };
  };
}
