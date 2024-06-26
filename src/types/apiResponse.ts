export interface BaseResponse {
  code: number;
  message?: string;
  token?: string;
}

export interface ApiResponse<T> extends BaseResponse {
  data: T;
}

export interface PageResponse<T> extends BaseResponse {
  data: {
    items: T[];
    total: number;
    pages: number;
  };
}
