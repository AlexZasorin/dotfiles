{ pkgs, ... }: {
  environment.systemPackages = with pkgs; [
    # Development tools
    cargo
    cargo-watch
    clippy
    helix
    jsonnet
    nodejs_20
    pnpm
    python313
    python313Packages.pip
    rustup
    zig
  ];
}
