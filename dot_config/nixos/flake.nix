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
          ./configuration.nix
          ./graphics/nvidia.nix
          ./desktop.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
      laptop = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./configuration.nix
          ./graphics/radeon.nix
          ./laptop.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
      default = nixpkgs.lib.nixosSystem {
        specialArgs = {inherit inputs;};
        modules = [
          ./configuration.nix
          ./secrets.nix
          # inputs.home-manager.nixosModules.default
        ];
      };
    };
    
    homeConfigurations."solyx" = home-manager.lib.homeManagerConfiguration {
      inherit pkgs;
      modules = [
        ./wsl/arch/home.nix
      ];
    };
  };
}
