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
    flyctl
    git-filter-repo
    helix
    zulu23
    jsonnet
    just
    nodejs_22
    playwright-driver.browsers
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

  environment.sessionVariables = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = "true";
  };
}
