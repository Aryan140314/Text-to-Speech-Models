import { app, BrowserWindow, ipcMain, shell } from 'electron';
import path from 'path';
import { backendManager } from './services/backendManager';

let mainWindow: BrowserWindow | null = null;
let backendPort: number = 8000;

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1380,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'TTS Studio — ElevenLabs Local Alternative',
    backgroundColor: '#090d16',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  mainWindow.setMenu(null);

  const isDev = process.env.NODE_ENV !== 'production';

  if (isDev) {
    await mainWindow.loadURL('http://localhost:5173');
  } else {
    await mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Register IPC handlers securely
ipcMain.handle('get-backend-port', () => backendPort);
ipcMain.handle('get-app-version', () => app.getVersion());
ipcMain.handle('open-output-folder', async (_, folderPath: string) => {
  if (folderPath) {
    shell.openPath(folderPath);
    return true;
  }
  return false;
});

app.whenReady().then(async () => {
  try {
    backendPort = await backendManager.startBackend();
  } catch (err) {
    console.error('[Electron Main] Failed starting backend service:', err);
  }
  await createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  backendManager.stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
