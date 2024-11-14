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
    python312
    python312Packages.pip
    rustup
    zig
  ];
}
