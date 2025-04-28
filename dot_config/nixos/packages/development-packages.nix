{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Development tools
    android-studio
    basedpyright
    cargo
    cargo-audit
    cargo-watch
    cargo-tarpaulin
    claude-code
    direnv
    git-filter-repo
    helix
    zulu23
    jsonnet
    just
    nodejs_22
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
