{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Development tools
    basedpyright
    cargo
    cargo-audit
    cargo-watch
    cargo-tarpaulin
    claude-code
    direnv
    git-filter-repo
    helix
    jsonnet
    just
    nodejs_22
    poetry
    pnpm
    python311
    python312
    python313
    python313Packages.pip
    pyright
    rustup
    uv
    zig
  ];
}
