import { ApiError } from './exceptions';
import { ApiErrorData } from './types';

export class HttpClient {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private async request<T>(
    url: string,
    method: 'GET' | 'POST' | 'DELETE' | 'PUT' = 'GET',
    payload: object | null = null
  ): Promise<T> {
    const options: RequestInit = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.token,
      },
      body: payload ? JSON.stringify(payload) : null,
    };

    const response = await fetch(url, options);

    if (!response.ok) {
      let data: ApiErrorData;

      try {
        data = await response.json();
      } catch {
        data = { error: response.statusText };
      }

      throw new ApiError(response.status, data.error);
    }

    return response.json();
  }

  public async get<T>(url: string) {
    return this.request<T>(url);
  }

  public async post<T>(url: string, payload: object | null = null) {
    return this.request<T>(url, 'POST', payload);
  }

  public async put<T>(url: string, payload: object | null = null) {
    return this.request<T>(url, 'PUT');
  }

  public async delete<T>(url: string) {
    return this.request<T>(url, 'DELETE');
  }
}
