{
  description = "Nixos config flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    sops-nix.url = "github:Mic92/sops-nix";
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
        ];
      };

      laptop = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./configurations/configuration.nix
          ./configurations/laptop.nix
        ];
      };

      server = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        system = "x86_64-linux";
        modules = [
          ./packages/base-packages.nix
          ./packages/development-packages.nix
          ./configurations/server.nix
        ];
      };

      default = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./configurations/configuration.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
    };
  };
}
