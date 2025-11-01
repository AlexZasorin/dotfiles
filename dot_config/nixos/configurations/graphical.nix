# TODO: Move over all non-package graphical configuration here
{
  pkgs,
  config,
  ...
}: {
  security.pam.services = {
    login = {
      kwallet.enable = true;
    };
  };
}
