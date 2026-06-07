/**
 * Returns a promise that resolves at the start of the next animation frame.
 * The promise resolves with the timestamp provided by the browser.
 */
export function nextFrame() {
  return new Promise((resolve) => requestAnimationFrame(resolve));
}

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
