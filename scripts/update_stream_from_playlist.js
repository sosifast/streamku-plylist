#!/usr/bin/env node
/*
  Update stream.json from playlist.m3u8 using api_image.json for image_url.
  - Parses EXTINF lines to extract channel name and the following URL line for stream.
  - Uses api_image.json mapping (case-insensitive) to determine image_url. Falls back to
    https://ik.imagekit.io/bfrfvbniv/streamku.png if not found.
  - Slug is generated from the channel name.
  - id_category defaults to 3 for new entries.
*/
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const streamPath = path.join(repoRoot, 'stream.json');
const playlistPath = path.join(repoRoot, 'playlist.m3u8');
const apiImagePath = path.join(repoRoot, 'api_image.json');

function slugify(name) {
  return String(name).toLowerCase().trim().replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

function imageUrlFor(name, imageMap) {
  if (!name) return 'https://ik.imagekit.io/bfrfvbniv/streamku.png';
  const key = name.toString().toLowerCase().trim();
  if (imageMap && Object.prototype.hasOwnProperty.call(imageMap, key)) {
    let rel = imageMap[key];
    if (typeof rel === 'string') {
      // Normalize to a single path after base
      rel = rel.replace(/^\//, '');
      // Base URL used in existing stream.json entries
      const base = 'https://jaruba.github.io/channel-logos/export/transparent-color/';
      // If already an absolute URL, return as is
      if (rel.startsWith('http://') || rel.startsWith('https://')) {
        return rel;
      }
      return base + rel;
    }
  }
  return 'https://ik.imagekit.io/bfrfvbniv/streamku.png';
}

function main() {
  let streams = [];
  try {
    const raw = fs.readFileSync(streamPath, 'utf-8');
    streams = JSON.parse(raw);
  } catch (e) {
    console.error('Failed reading/parsing stream.json:', e.message);
    process.exit(1);
  }

  // Load image map from api_image.json; handle header line and JSON body
  let imageMap = {};
  try {
    const rawMap = fs.readFileSync(apiImagePath, 'utf-8');
    const start = rawMap.indexOf('{');
    const end = rawMap.lastIndexOf('}');
    if (start >= 0 && end >= start) {
      const jsonText = rawMap.substring(start, end + 1);
      imageMap = JSON.parse(jsonText);
    }
  } catch (e) {
    console.warn('Warning: could not parse api_image.json, image URLs may fall back to default.');
    imageMap = {};
  }

  // Read playlist and extract channel entries
  let playlist = [];
  try {
    const plRaw = fs.readFileSync(playlistPath, 'utf-8');
    const lines = plRaw.split(/\r?\n/);
    for (let i = 0; i < lines.length - 1; i++) {
      const line = lines[i].trim();
      if (line.startsWith('#EXTINF')) {
        // Extract channel name after the last comma
        const commaIndex = line.lastIndexOf(',');
        let name = commaIndex >= 0 ? line.substring(commaIndex + 1).trim() : '';
        // Clean up possible (1080p) suffix or extra text
        name = name.replace(/\s*\(.*\)\s*$/, '').trim();
        // Next line should be the URL
        const urlLine = lines[i + 1] ? lines[i + 1].trim() : '';
        if (name && urlLine) {
          playlist.push({ name, url: urlLine });
        }
      }
    }
  } catch (e) {
    console.error('Failed reading playlist.m3u8:', e.message);
    process.exit(1);
  }

  if (playlist.length === 0) {
    console.log('No entries found in playlist.m3u8. Nothing to update.');
    process.exit(0);
  }

  // Build new entries from playlist
  const existingMaxId = streams.reduce((m, s) => Math.max(m, s && s.id ? s.id : 0), 0);
  let nextId = existingMaxId + 1;
  const baseCategory = 3;

  const toAdd = playlist.map(item => {
    const name = item.name;
    const slug = slugify(name);
    const image_url = imageUrlFor(name, imageMap);
    const seo_title = `Watch ${name} Live TV on Streamku – Free HD Streaming`;
    const desc_title = `Watch ${name} live TV on Streamku with high-quality HD streaming.`;
    const url_stream = item.url;
    return {
      id: nextId++,
      name,
      slug,
      seo_title,
      desc_title,
      image_url,
      url_stream,
      id_category: baseCategory
    };
  });

  // Append to existing streams and write back
  const updated = streams.concat(toAdd);
  try {
    fs.writeFileSync(streamPath, JSON.stringify(updated, null, 2) + '\n', 'utf-8');
    console.log(`Appended ${toAdd.length} streams to stream.json`);
  } catch (e) {
    console.error('Failed writing stream.json:', e.message);
    process.exit(1);
  }
}

main();
