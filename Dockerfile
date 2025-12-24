# Builds himnario.pdf without installing pandoc/LaTeX (and tlmgr as root) on the host.
# Usage: just pdf-docker   (or manually: <engine> build -t hymns-pdf . && <engine> run --rm -v "$(pwd)":/data hymns-pdf)
FROM --platform=linux/amd64 pandoc/latex:latest

RUN apk add --no-cache bash && \
    tlmgr update --self && \
    tlmgr install titlesec fancyhdr parskip etoolbox ebgaramond gillius extsizes fontaxes

WORKDIR /data
ENTRYPOINT ["bash", "scripts/build-pdf.sh"]
