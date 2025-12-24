# Hymns

Digital hymnary project supporting static website generation (Hugo) and PDF output.

### Prerequisites Setup (macOS)

You will need **Homebrew** installed.

```bash
# 1. Install Hugo
brew install hugo

# 2. Install Pandoc (for PDF)
brew install pandoc

# 3. Install LaTeX (BasicTeX is enough, ~100MB vs 2GB for MacTeX)
brew install --cask basictex

# 4. Install required LaTeX packages
# After installing BasicTeX, you might need these packages for the template
sudo tlmgr update --self
sudo tlmgr install titlesec fancyhdr parskip etoolbox ms ebgaramond gillius
```

## Local Development

To start the development server and view the site in real-time:

```bash
hugo server -D
```

The site will be available at `http://localhost:1313/`.

## Build

To generate the static site for production (`public/` folder):

```bash
hugo --minify
```

## PDF

To generate the hymnary PDF (requires `build-pdf.sh` script and dependencies):

```bash
./build-pdf.sh
```

## License

Code under MIT License. See [LICENSE](LICENSE) for details.
**Note:** Content (hymn lyrics) copyright belongs to their respective authors.
