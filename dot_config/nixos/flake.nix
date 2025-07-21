{
  description = "Nixos config flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/5af573cc81d977daffa9ca6ba2e1761256e6e562";
    nixos-wsl.url = "github:nix-community/NixOS-WSL/main";
  };

  outputs = {
    self,
    nixpkgs,
    nixos-wsl,
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
          ./graphics/nvidia.nix
          ./configurations/configuration.nix
          ./configurations/desktop.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
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
          # inputs.home-manager.nixosModules.default
        ];
      };

      wsl = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        system = "x86_64-linux";
        modules = [
          nixos-wsl.nixosModules.default
          ./packages/base-packages.nix
          ./packages/development-packages.nix
          ./packages/system-packages/wsl.nix
          ./configurations/wsl.nix
          ./secrets.nix
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
