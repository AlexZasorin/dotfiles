{
  pkgs,
  config,
  ...
}: {
  nix.settings.access-tokens = "!include ~/.github-token";
  networking.hostName = "phobos"; # Define your hostname.
}
