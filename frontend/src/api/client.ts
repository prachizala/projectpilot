const API_BASE = '/api/v1';

class ApiClient {
  private getAccessToken(): string | null {
    return localStorage.getItem('projectpilot_access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('projectpilot_refresh_token');
  }

  private setTokens(access: string, refresh: string) {
    localStorage.setItem('projectpilot_access_token', access);
    localStorage.setItem('projectpilot_refresh_token', refresh);
  }

  public clearTokens() {
    localStorage.removeItem('projectpilot_access_token');
    localStorage.removeItem('projectpilot_refresh_token');
    localStorage.removeItem('projectpilot_user');
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getAccessToken();
    const headers = new Headers(options.headers || {});
    headers.set('Content-Type', 'application/json');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    let response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle token expiration: attempt automatic refresh
    if (response.status === 401 && this.getRefreshToken()) {
      try {
        const refreshResp = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: this.getRefreshToken() }),
        });

        if (refreshResp.ok) {
          const tokenData = await refreshResp.json();
          this.setTokens(tokenData.access_token, tokenData.refresh_token);
          // Retry original request with fresh token
          headers.set('Authorization', `Bearer ${tokenData.access_token}`);
          response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
          });
        } else {
          this.clearTokens();
          window.location.href = '/login';
        }
      } catch {
        this.clearTokens();
        window.location.href = '/login';
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network response was not ok' }));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth Endpoints
  public async signup(data: any) {
    const res = await this.request<any>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setTokens(res.access_token, res.refresh_token);
    localStorage.setItem('projectpilot_user', JSON.stringify(res.user));
    return res;
  }

  public async login(data: any) {
    const res = await this.request<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setTokens(res.access_token, res.refresh_token);
    localStorage.setItem('projectpilot_user', JSON.stringify(res.user));
    return res;
  }

  public async getMe() {
    return this.request<any>('/auth/me');
  }

  // Clients Endpoints
  public async getClients(search?: string) {
    const query = search ? `?q=${encodeURIComponent(search)}` : '';
    return this.request<any[]>(`/clients${query}`);
  }

  public async createClient(data: any) {
    return this.request<any>('/clients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async updateClient(id: number, data: any) {
    return this.request<any>(`/clients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  public async deleteClient(id: number) {
    return this.request<any>(`/clients/${id}`, {
      method: 'DELETE',
    });
  }

  // Projects Endpoints
  public async getProjects(status?: string, clientId?: number) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (clientId) params.append('client_id', clientId.toString());
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<any[]>(`/projects${query}`);
  }

  public async createProject(data: any) {
    return this.request<any>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async updateProject(id: number, data: any) {
    return this.request<any>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  public async deleteProject(id: number) {
    return this.request<any>(`/projects/${id}`, {
      method: 'DELETE',
    });
  }

  // Tasks & Kanban Endpoints
  public async getProjectTasks(projectId: number) {
    return this.request<any[]>(`/projects/${projectId}/tasks`);
  }

  public async createTask(projectId: number, data: any) {
    return this.request<any>(`/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  public async updateTaskPosition(taskId: number, data: { status: string; position: number }) {
    return this.request<any>(`/tasks/${taskId}/position`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  public async deleteTask(taskId: number) {
    return this.request<any>(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();
