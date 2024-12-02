{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Development tools
    cargo
    cargo-audit
    cargo-watch
    cargo-tarpaulin
    helix
    jsonnet
    just
    nodejs_20
    poetry
    pnpm
    python313
    python313Packages.pip
    rustup
    uv
    zig
  ];
}
