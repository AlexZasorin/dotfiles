{ pkgs, ... }: {
  environment.systemPackages = with pkgs; [
    # Development tools
    cargo
    helix
    jsonnet
    nodejs_20
    pnpm
    python312
    python312Packages.pip
    zig
  ];
}
