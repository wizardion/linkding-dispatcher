export class ApiError extends Error {
  status: number;
  message: string;

  constructor(status: number, message: string) {
    super(message || `HTTP Error ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.message = message;
  }
}
