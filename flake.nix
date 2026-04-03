{
  description = "AirSpace";
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
      ];
    };

      services.yggdrasil = {
        enable         = true;
        persistentKeys = true;
        settings = {
          Peers = [
            "quic://185.181.60.111:1513?key=00defa4b4b243547f2d5641ac5235ff1e35d393c576e4bb9cd45baefc81e48d9"
            "tls://185.181.60.111:1513?key=00defa4b4b243547f2d5641ac5235ff1e35d393c576e4bb9cd45baefc81e48d9"
          ];
          Listen = [
            "tls://0.0.0.0:12345"
          ];
        };
      };
    };
  };
}
