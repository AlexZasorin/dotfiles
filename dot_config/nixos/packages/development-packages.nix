{pkgs, ...}: {
  environment.systemPackages = with pkgs; [
    # Development tools
    android-studio
    basedpyright
    cargo
    cargo-audit
    cargo-tarpaulin
    cargo-watch
    chromium
    claude-code
    direnv
    flyctl
    git-filter-repo
    helix
    jsonnet
    just
    nodejs_24
    playwright-driver.browsers
    pnpm
    prisma-engines
    pyright
    python313
    python313Packages.pip
    rustup
    uv
    zig
    zulu
  ];

  environment.variables = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = "true";
    PUPPETEER_SKIP_DOWNLOAD = "1"; # Skip downloading Chromium for Puppeteer
    PUPPETEER_EXECUTABLE_PATH = "${pkgs.chromium}/bin/chromium"; # Use system Chromium

    PRISMA_SCHEMA_ENGINE_BINARY = "${pkgs.prisma-engines}/bin/schema-engine";
    PRISMA_QUERY_ENGINE_BINARY = "${pkgs.prisma-engines}/bin/query-engine";
    PRISMA_QUERY_ENGINE_LIBRARY = "${pkgs.prisma-engines}/lib/libquery_engine.node";
    PRISMA_FMT_BINARY = "${pkgs.prisma-engines}/bin/prisma-fmt";
  };
}
