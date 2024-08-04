{
  config,
  lib,
  pkgs,
  ...
}: let
  # Path to the GitHub token file
  githubTokenPath = "/etc/nixos/.github-token";
in {
  nix.settings = {
    access-tokens = lib.mkIf (builtins.pathExists githubTokenPath) [
      "github.com=${builtins.readFile githubTokenPath}"
    ];
  };

  # Ensure the token file exists and has correct permissions
  system.activationScripts.ensureGithubTokenFile = ''
    if [ ! -f ${githubTokenPath} ]; then
      touch ${githubTokenPath}
      chmod 600 ${githubTokenPath}
      chown root:root ${githubTokenPath}
    fi
  '';
}
