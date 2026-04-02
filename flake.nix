{
  description = "AirSpace dev shell";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devShells.${system}.default = pkgs.mkShell {
      name = "airspace";
      packages = with pkgs; [
        python3
        python3Packages.pyyaml
        python3Packages.rich
        radicale
      ];

    };
  };
}
