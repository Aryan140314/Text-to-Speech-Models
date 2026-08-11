import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import net from 'net';
import fs from 'fs';
import { app } from 'electron';
import { checkBackendHealth } from './backendHealth';

export class BackendManager {
  private backendProcess: ChildProcess | null = null;
  private backendPort: number = 8000;

  public async getAvailablePort(): Promise<number> {
    return new Promise((resolve) => {
      const server = net.createServer();
      server.listen(0, '127.0.0.1', () => {
        const port = (server.address() as net.AddressInfo).port;
        server.close(() => resolve(port));
      });
    });
  }

  public async startBackend(): Promise<number> {
    this.backendPort = await this.getAvailablePort();
    console.log(`[Electron Main] Spawning Python Backend on dynamic port ${this.backendPort}...`);

    const isPackaged = app ? app.isPackaged : process.env.NODE_ENV === 'production';
    const rootDir = path.resolve(__dirname, '../../..');

    if (isPackaged) {
      const exePath = path.join(process.resourcesPath, 'backend', 'tts_backend.exe');
      console.log(`[Electron Main] Launching packaged backend executable: ${exePath}`);
      if (fs.existsSync(exePath)) {
        this.backendProcess = spawn(exePath, ['--port', this.backendPort.toString()], {
          cwd: path.dirname(exePath),
        });
      } else {
        console.error(`[Electron Main] Packaged executable not found at ${exePath}!`);
      }
    } else {
      const pythonExe = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
      const scriptPath = path.join(rootDir, 'backend', 'app', 'main.py');
      console.log(`[Electron Main] Launching dev python script: ${scriptPath}`);

      this.backendProcess = spawn(pythonExe, [scriptPath, '--port', this.backendPort.toString()], {
        cwd: rootDir,
        env: { ...process.env, TTS_PORTABLE_DEV: '1', PYTHONPATH: rootDir },
      });
    }

    if (this.backendProcess) {
      this.backendProcess.stdout?.on('data', (data) => {
        console.log(`[Python stdout]: ${data.toString().trim()}`);
      });

      this.backendProcess.stderr?.on('data', (data) => {
        console.error(`[Python stderr]: ${data.toString().trim()}`);
      });

      this.backendProcess.on('exit', (code) => {
        console.log(`[Python Backend] Exited with code ${code}`);
      });
    }

    // Poll health until ready
    let attempts = 0;
    while (attempts < 30) {
      const healthy = await checkBackendHealth(this.backendPort);
      if (healthy) {
        console.log(`[Electron Main] Python Backend READY at http://127.0.0.1:${this.backendPort}`);
        return this.backendPort;
      }
      await new Promise((res) => setTimeout(res, 500));
      attempts++;
    }

    console.warn('[Electron Main] Python Backend did not respond within health check timeout');
    return this.backendPort;
  }

  public stopBackend(): void {
    if (this.backendProcess) {
      console.log('[Electron Main] Killing Python Backend process...');
      this.backendProcess.kill();
      this.backendProcess = null;
    }
  }

  public getPort(): number {
    return this.backendPort;
  }
}

export const backendManager = new BackendManager();
