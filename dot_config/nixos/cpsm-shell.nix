{pkgs ? import <nixpkgs> {}}:
pkgs.mkShell {
  packages = with pkgs; [
    cmake
    python3
    boost
  ];

  inputsFrom = [
    pkgs.boost
    pkgs.python3
  ];
}
