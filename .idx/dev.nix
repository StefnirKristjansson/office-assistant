{ pkgs, ... }: {
  # Specify the Nixpkgs channel
  channel = "stable-23.11";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.virtualenv
    pkgs.sudo
    pkgs.postgresql_14
    pkgs.gcc
    pkgs.libxml2
    pkgs.libxslt
  ];

  # Set environment variables in the workspace
  env = { };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      "ms-python.debugpy"
      "ms-python.python"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["sh" "-c" "source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port $PORT"];
          manager = "web";
          env = {
            PORT = "$PORT";
          };
        };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        setup = ''
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
        '';
      };

      # Runs when the workspace is (re)started
      onStart = {
        setup = ''
          source venv/bin/activate
        '';
      };
    };
  };
}
