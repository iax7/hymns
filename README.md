# Hymns

Digital hymnary project supporting static website generation (Hugo) and PDF output.

## Prerequisites Setup (macOS)

You will need **Homebrew** installed.

```bash
# Install dependencies
brew install hugo pandoc

# Install LaTeX (BasicTeX is enough, ~100MB vs 2GB for MacTeX)
brew install --cask basictex

# Install required LaTeX packages
# After installing BasicTeX, you might need these packages for the template
sudo tlmgr update --self
sudo tlmgr install titlesec fancyhdr parskip etoolbox ebgaramond gillius extsizes fontaxes

# Install Python dependencies (used by scripts/generate_image.py and scripts/list-hymns.py)
pip3 install -r requirements.txt
```

## Local Development

To start the development server and view the site in real-time:

```bash
just serve
```

The site will be available at `http://localhost:1313/`.

## Build

To generate the static site for production (`public/` folder):

```bash
just build
```

## PDF

To generate the hymnary PDF (requires `build-pdf.sh` script and dependencies):

```bash
just pdf
```

### PDF via container (no root/tlmgr install on your machine)

If you'd rather not run `sudo tlmgr install ...` on your host, build and run the PDF toolchain (Pandoc + LaTeX) inside a container instead:

```bash
just pdf-docker
```

This builds an image from the `Dockerfile` (based on `pandoc/latex`, with the required LaTeX packages installed inside the container) and runs `scripts/build-pdf.sh` against your working copy, writing `himnario.pdf` to the repo root. It uses `docker` by default; pass `podman` as an argument to use Podman instead:

```bash
just pdf-docker podman
```

Equivalent to:

```bash
docker build -t hymns-pdf .
docker run --rm -v "$(pwd)":/data hymns-pdf
```

#### Troubleshooting: Podman short-name resolution

Docker implicitly prefixes unqualified image names with `docker.io`, but Podman requires a configured list of search registries. Without one, `just pdf-docker podman` fails with:

```
Error: creating build container: short-name "pandoc/latex:latest" did not resolve to an alias
and no containers-registries.conf(5) was found
```

Fix it by creating `~/.config/containers/registries.conf` (user-wide) or `/etc/containers/registries.conf` (system-wide):

```toml
unqualified-search-registries = ["docker.io"]
short-name-mode = "permissive"
```

This makes Podman resolve `pandoc/latex:latest` exactly as Docker would. Verify with:

```bash
podman pull pandoc/latex:latest
```

## License

Code under MIT License. See [LICENSE](LICENSE) for details.
**Note:** Content (hymn lyrics) copyright belongs to their respective authors.
