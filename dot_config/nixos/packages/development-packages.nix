{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Development tools
    basedpyright
    cargo
    cargo-audit
    cargo-watch
    cargo-tarpaulin
    direnv
    helix
    jsonnet
    just
    nodejs_20
    poetry
    pnpm
    python313
    python313Packages.pip
    pyright
    rustup
    uv
    zig
  ];
}
