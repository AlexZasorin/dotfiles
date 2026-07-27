# Shared restic -> Backblaze B2 backup config.
# Per-host paths are set in the host modules (desktop.nix / laptop.nix / server.nix).
# The repo password is provided via sops; add the value to secrets.yaml as `restic_password`.
{config, ...}: {
  # Runs as root (the restic service default), so root-owned 0400 is correct.
  sops.secrets.restic_password = {};

  services.restic.backups.b2 = {
    initialize = true;
    # Each host gets its own prefix in the bucket via the hostname.
    repository = "b2:CHANGE_ME_BUCKET:${config.networking.hostName}";
    passwordFile = config.sops.secrets.restic_password.path;

    # Filled in per-host.
    paths = [];

    timerConfig = {
      OnCalendar = "daily";
      Persistent = true;
      RandomizedDelaySec = "1h";
    };

    pruneOpts = [
      "--keep-daily 7"
      "--keep-weekly 4"
      "--keep-monthly 6"
    ];
  };
}
