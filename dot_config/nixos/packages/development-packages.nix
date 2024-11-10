{ pkgs, ... }: {
  base-packages = with pkgs; [
    # Development tools
    cargo
    helix
    jsonnet
    nodejs_20
    pnpm
    python313
    python313Packages.pip
    zig
}
