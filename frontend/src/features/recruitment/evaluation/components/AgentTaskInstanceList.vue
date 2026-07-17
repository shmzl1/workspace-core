<template>
  <TransitionGroup name="task-instance" tag="div" class="task-instance-list">
    <div
      v-for="instance in instances"
      :key="instance.candidateId ?? instance.label"
      class="task-instance-row"
      :class="{ 'task-instance-row--running': instance.status === 'RUNNING' }"
    >
      <span class="task-status-dot" :class="`task-status-dot--${instance.status.toLowerCase()}`" aria-hidden="true"></span>
      <span class="task-instance-label" :title="instance.label">{{ instance.label }}</span>
      <span class="task-instance-status" :class="`task-instance-status--${instance.status.toLowerCase()}`">
        {{ statusLabel(instance.status) }}
      </span>
      <span v-if="instance.durationMs !== null" class="task-instance-duration">
        {{ formatDuration(instance.durationMs) }}
      </span>
    </div>
  </TransitionGroup>
</template>

<script setup lang="ts">
import type {
  AgentTaskInstance,
  AgentTaskInstanceStatus,
} from '../utils/agentTaskInstances';

defineProps<{ instances: AgentTaskInstance[] }>();

function statusLabel(status: AgentTaskInstanceStatus): string {
  return {
    WAITING: '等待中',
    RUNNING: '运行中',
    COMPLETED: '已完成',
    NEEDS_REVIEW: '需要复核',
    FAILED: '失败',
  }[status];
}

function formatDuration(durationMs: number): string {
  return durationMs < 1000 ? `${durationMs}ms` : `${(durationMs / 1000).toFixed(1)}s`;
}
</script>

<style scoped>
.task-instance-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.task-instance-row {
  position: relative;
  display: grid;
  grid-template-columns: 8px minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  padding: 0 6px;
  border-radius: 8px;
  overflow: hidden;
  color: #475569;
  font-size: 11px;
}

.task-instance-row--running {
  background: linear-gradient(90deg, rgba(219, 234, 254, 0.72), rgba(239, 246, 255, 0.18));
}

.task-instance-row--running::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.13), transparent);
  transform: translateX(-100%);
  animation: currentTaskSweep 1.8s ease-out infinite;
  pointer-events: none;
}

.task-status-dot {
  z-index: 1;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #cbd5e1;
}

.task-status-dot--running {
  background: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.13);
  animation: currentTaskPulse 1.6s ease-in-out infinite;
}

.task-status-dot--completed { background: #10b981; }
.task-status-dot--needs_review { background: #f59e0b; }
.task-status-dot--failed { background: #ef4444; }

.task-instance-label {
  z-index: 1;
  min-width: 0;
  overflow: hidden;
  color: #334155;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-instance-status,
.task-instance-duration {
  z-index: 1;
  white-space: nowrap;
}

.task-instance-status--running { color: #2563eb; }
.task-instance-status--completed { color: #059669; }
.task-instance-status--needs_review { color: #d97706; }
.task-instance-status--failed { color: #dc2626; }
.task-instance-status--waiting { color: #94a3b8; }

.task-instance-duration {
  min-width: 34px;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.task-instance-enter-active,
.task-instance-leave-active,
.task-instance-move {
  transition: opacity 180ms ease, transform 180ms ease;
}

.task-instance-enter-from,
.task-instance-leave-to {
  opacity: 0;
  transform: translateY(3px);
}

@keyframes currentTaskPulse {
  0%, 100% { opacity: 0.62; }
  50% { opacity: 1; }
}

@keyframes currentTaskSweep {
  to { transform: translateX(100%); }
}

[data-theme="dark"] .task-instance-row { color: #94a3b8; }
[data-theme="dark"] .task-instance-row--running {
  background: linear-gradient(90deg, rgba(30, 58, 95, 0.72), rgba(30, 41, 59, 0.1));
}
[data-theme="dark"] .task-instance-label { color: #cbd5e1; }
</style>
