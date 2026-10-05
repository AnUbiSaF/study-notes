#!/usr/bin/env bash
set -euo pipefail

site_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
vault_dir="$(cd "${site_dir}/.." && pwd)"
content_dir="${site_dir}/content"

mkdir -p "${content_dir}"
rsync -a --delete --delete-excluded \
  --exclude '/.quartz-site/' \
  --exclude '/.obsidian/' \
  --exclude '/.pnpm-store/' \
  --exclude '/_backups/' \
  --exclude '/Шаблоны/' \
  --exclude '/Машинное обучение/' \
  --exclude '.DS_Store' \
  --exclude '*.canvas' \
  --exclude '/00 — Карта предметов.md' \
  "${vault_dir}/" "${content_dir}/"

cp "${vault_dir}/00 — Карта предметов.md" "${content_dir}/index.md"

index_tmp="${content_dir}/.index.md.tmp"
{
  printf '%s\n' '---' 'title: Учёба' '---'
  cat "${content_dir}/index.md"
} > "${index_tmp}"
mv "${index_tmp}" "${content_dir}/index.md"

# Раздел ML пока не публикуется и не должен оставлять битую ссылку на главной.
sed -i '' '/^- \[\[Машинное обучение\]\]$/d' "${content_dir}/index.md"

# В опубликованной копии главная карта называется index.md.
# Меняется только адрес ссылки; текст и смысл заметок остаются прежними.
find "${content_dir}" -type f -name '*.md' -exec \
  sed -i '' 's/\[\[00 — Карта предметов|/[[index|/g' {} +

printf 'Содержимое Quartz синхронизировано из Obsidian.\n'
