{
  description = "Nixos config flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    self,
    nixpkgs,
    home-manager,
    ...
  } @ inputs:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      config = {
        allowUnfree = true;
      };
    };
  in
  {
    nixosConfigurations = {
      desktop = nixpkgs.lib.nixosSystem {
        specialArgs = { inherit inputs; };
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./graphics/nvidia.nix
          ./configurations/default.nix
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
          ./graphics/radeon.nix
          ./configurations/default.nix
          ./configurations/laptop.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
      default = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./packages/default.nix
          ./packages/system-packages/nixos.nix
          ./configurations/default.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
    };
    
    homeConfigurations."arch" = home-manager.lib.homeManagerConfiguration {
      inherit pkgs;
      modules = [
        ./configurations/wsl/arch.nix
      ];
    };
  };
}
