{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
        app = python.pkgs.buildPythonApplication {
          pname = "voicevox-claude";
          version = "0.1.0";
          src = ./.;
          pyproject = true;
          build-system = with python.pkgs; [ setuptools setuptools-scm ];
          dependencies = with python.pkgs; [
            mcp
            httpx
          ];
          nativeBuildInputs = [ pkgs.makeWrapper ];
          postFixup = ''
            wrapProgram $out/bin/voicevox-claude \
              --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.pipewire pkgs.pulseaudio pkgs.alsa-utils pkgs.ffmpeg ]}
          '';
        };
      in
      {
        packages.default = app;
      }
    );
}
