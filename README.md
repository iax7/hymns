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

### PDF via Docker (no root/tlmgr install on your machine)

If you'd rather not run `sudo tlmgr install ...` on your host, build and run the PDF toolchain (Pandoc + LaTeX) inside Docker instead:

```bash
just pdf-docker
```

This builds an image from the `Dockerfile` (based on `pandoc/latex`, with the required LaTeX packages installed inside the container) and runs `scripts/build-pdf.sh` against your working copy, writing `himnario.pdf` to the repo root. Equivalent to:

```bash
docker build -t hymns-pdf .
docker run --rm -v "$(pwd)":/data hymns-pdf
```

## License

Code under MIT License. See [LICENSE](LICENSE) for details.
**Note:** Content (hymn lyrics) copyright belongs to their respective authors.
