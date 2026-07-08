/**
 * useAsyncData — 统一异步数据状态管理
 *
 * 封装 loading / error / data / empty 四种核心状态，
 * 让视图层无需重复编写 try-catch 和状态标志位。
 *
 * @example
 * ```ts
 * const { data, loading, error, isEmpty, execute, retry } = useAsyncData(
 *   () => fetchCandidates({ job_id: 1 })
 * );
 * onMounted(() => execute());
 * ```
 */
import { ref, computed, type Ref, type ComputedRef } from 'vue';

export interface AsyncDataState<T> {
  /** 当前数据 */
  data: Ref<T | null>;
  /** 是否正在加载 */
  loading: Ref<boolean>;
  /** 错误信息（null 表示无错误） */
  error: Ref<string | null>;
  /** 是否为权限拒绝（HTTP 403） */
  permissionDenied: Ref<boolean>;
  /** 数据是否为空（null、undefined 或空数组） */
  isEmpty: ComputedRef<boolean>;
  /** 触发数据获取 */
  execute: () => Promise<T | null>;
  /** 重试（等同于 execute） */
  retry: () => Promise<T | null>;
  /** 手动设置数据（用于乐观更新等场景） */
  setData: (value: T | null) => void;
}

export function useAsyncData<T>(
  fetcher: () => Promise<T>,
): AsyncDataState<T> {
  const data = ref<T | null>(null) as Ref<T | null>;
  const loading = ref(false);
  const error = ref<string | null>(null);
  const permissionDenied = ref(false);

  const isEmpty = computed(() => {
    const d = data.value;
    if (d === null || d === undefined) return true;
    if (Array.isArray(d) && d.length === 0) return true;
    return false;
  });

  async function execute(): Promise<T | null> {
    loading.value = true;
    error.value = null;
    permissionDenied.value = false;

    try {
      const result = await fetcher();
      data.value = result;
      return result;
    } catch (e: unknown) {
      const msg = extractErrorMessage(e);
      error.value = msg;

      // 判断是否为权限拒绝
      if (isPermissionDenied(e)) {
        permissionDenied.value = true;
      }

      data.value = null;
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function retry(): Promise<T | null> {
    return execute();
  }

  function setData(value: T | null): void {
    data.value = value;
  }

  return {
    data,
    loading,
    error,
    permissionDenied,
    isEmpty,
    execute,
    retry,
    setData,
  };
}

// ── 辅助函数 ─────────────────────────────────

function extractErrorMessage(e: unknown): string {
  if (!e) return '未知错误';
  if (typeof e === 'string') return e;

  const obj = e as Record<string, unknown>;

  // Axios error
  if (obj.response && typeof obj.response === 'object') {
    const resp = obj.response as Record<string, unknown>;
    if (resp.data && typeof resp.data === 'object') {
      const d = resp.data as Record<string, unknown>;
      if (typeof d.message === 'string') return d.message;
      if (d.error && typeof d.error === 'object') {
        const err = d.error as Record<string, unknown>;
        if (typeof err.message === 'string') return err.message;
      }
    }
    if (typeof resp.statusText === 'string') return resp.statusText;
  }

  // 通用 message 字段
  if (typeof obj.message === 'string') return obj.message;
  if (typeof obj.code === 'string') return obj.code;

  return '请求失败，请稍后重试';
}

function isPermissionDenied(e: unknown): boolean {
  if (!e || typeof e !== 'object') return false;
  const obj = e as Record<string, unknown>;

  // Axios 403
  if (obj.response && typeof obj.response === 'object') {
    const resp = obj.response as Record<string, unknown>;
    if (resp.status === 403) return true;
  }

  // 业务层 PERMISSION_DENIED
  if (typeof obj.code === 'string') {
    const code = obj.code as string;
    if (code === 'PERMISSION_DENIED' || code === 'ACCESS_DENIED' || code === 'FORBIDDEN') {
      return true;
    }
  }

  return false;
}
