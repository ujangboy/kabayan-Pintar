// backend.mjs — jalankan uvicorn dengan interpreter venv PROYEK yang
// deterministik (.venv), bukan `python` polos yang mengikuti venv apa
// pun yang sedang aktif di shell user (akar bug RAG "tidak dikenali").
// Bila .venv tidak ada, fallback ke perilaku lama (python/python3).
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const candidates = [
  path.join(root, '.venv', 'bin', 'python'),
  path.join(root, '.venv', 'Scripts', 'python.exe'),
];
const python = candidates.find((p) => existsSync(p)) || (process.platform === 'win32' ? 'python' : 'python3');

const child = spawn(
  python,
  ['-m', 'uvicorn', 'app.main:app', '--port', '8000', '--reload'],
  { cwd: root, stdio: 'inherit' }
);
child.on('exit', (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exit(code ?? 0);
});
