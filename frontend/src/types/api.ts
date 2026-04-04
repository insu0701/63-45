export type ApiResponse<T> = {
  data: T;
  meta: {
    generated_at: string;
    snapshot_time: string | null;
  };
  errors: Array<{
    code?: string;
    message?: string;
  }>;
};