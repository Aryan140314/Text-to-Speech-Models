import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import net from 'net';
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

    const isPackaged = process.env.NODE_ENV === 'production';
    const rootDir = path.resolve(__dirname, '../../..');

    if (isPackaged) {
      const exePath = path.join(process.resourcesPath, 'backend', 'tts_backend.exe');
      this.backendProcess = spawn(exePath, ['--port', this.backendPort.toString()]);
    } else {
      const pythonExe = path.join(rootDir, '.venv', 'Scripts', 'python.exe');
      const scriptPath = path.join(rootDir, 'backend', 'app', 'main.py');

      this.backendProcess = spawn(pythonExe, [scriptPath, '--port', this.backendPort.toString()], {
        cwd: rootDir,
        env: { ...process.env, TTS_PORTABLE_DEV: '1', PYTHONPATH: rootDir },
      });
    }

    this.backendProcess.stdout?.on('data', (data) => {
      console.log(`[Python stdout]: ${data.toString().trim()}`);
    });

    this.backendProcess.stderr?.on('data', (data) => {
      console.error(`[Python stderr]: ${data.toString().trim()}`);
    });

    this.backendProcess.on('exit', (code) => {
      console.log(`[Python Backend] Exited with code ${code}`);
    });

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

    throw new Error('Python Backend failed to start within timeout');
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
