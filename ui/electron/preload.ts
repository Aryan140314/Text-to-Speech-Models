import { contextBridge, ipcRenderer } from 'electron';

export interface ElectronAPI {
  getBackendPort: () => Promise<number>;
  openOutputFolder: (folderPath: string) => Promise<boolean>;
  getAppVersion: () => Promise<string>;
}

const api: ElectronAPI = {
  getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
  openOutputFolder: (folderPath: string) => ipcRenderer.invoke('open-output-folder', folderPath),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
};

contextBridge.exposeInMainWorld('electronAPI', api);
